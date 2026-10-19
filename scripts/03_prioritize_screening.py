"""Screening support used during title-and-abstract screening (Sections 3.1-3.2, Limitations).

Two tools ordered the records and suggested a label. Final decisions are recorded in
data/screening/records_screened.csv; how the suggestions were used, including the
records reviewed in groups in the primary wave, is described in protocol/protocol.md (section 5).

  relevance score   TF-IDF cosine similarity between each record (title counted
                    twice, abstract, keywords) and a fixed query written from the
                    research questions, after terminology normalisation with the
                    VOSviewer thesaurus; rescaled 0-100 within the corpus.
  rule-based label  keyword patterns aligned with criteria I2, I3, I4, E1, E2, E5, E6
                    give a suggestion (include / uncertain / survey / exclude) and a
                    0-10 signal score. "include" and "uncertain" records always
                    went to a human reader.

The dictionaries, weights and thresholds below were fixed before screening and were
not changed for the complementary (R4) batch. Because scores are rescaled within the
corpus, R4 records were scored together with the primary records (2,708 in total)
and only the R4 rows were screened.

Needs data/interim/ from 02_deduplicate.py. Writes data/interim/prioritised_*.csv.
"""

import re

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from common import INTERIM, SCREENING, VOSVIEWER, Thesaurus

QUERY = """
neuro-symbolic semantic matching multilingual indicators heterogeneous
knowledge graph ontology explainable explainability interpretable justification
harmonization data integration monitoring evaluation
human-in-the-loop interactive validation expert feedback HITL
transformer embeddings BERT multilingual similarity
schema matching ontology matching ontology alignment entity alignment entity resolution
ex-post harmonization development indicators variable mapping
neuro-symbolic AI symbolic reasoning neural network hybrid neural symbolic
knowledge representation structured constraints logic rules
interpretability transparency reasoning traces
"""

I2_STRONG = [
    r'schema match', r'ontology match', r'ontology align', r'entity align', r'entity resolution',
    r'record linkage', r'data harmoniz', r'data harmonis', r'variable match', r'variable mapp',
    r'variable align', r'variable harmoniz', r'semantic match', r'semantic align', r'semantic harmoniz',
    r'knowledge align', r'knowledge match', r'indicator.*match', r'indicator.*harmoniz',
    r'indicator.*align', r'survey.*harmoniz', r'cross.?lingual.*match', r'multilingual.*match',
    r'heterogeneous.*match', r'heterogeneous.*align', r'column match', r'attribute match',
    r'table match', r'inter.?operab.*match', r'schema.*integrat',
]
I2_WEAK = [
    r'data integrat', r'semantic integrat', r'knowledge integrat', r'entity linking', r'entity match',
    r'cross.?lingual.*align', r'multilingual.*align', r'mapping.*hetero', r'heterogeneous.*integrat',
    r'semantic interoperab', r'data.*align',
]
I4_STRONG = [
    r'neuro.?symbolic', r'neural.?symbolic', r'neurosymbolic', r'hybrid.*neural.*symbol',
    r'hybrid.*symbol.*neural', r'neural.*symbolic.*reason', r'symbolic.*reason.*neural',
    r'logic.*neural.*network', r'neural.*logic.*rule',
]
I4_WEAK = [
    r'knowledge graph.*embed', r'embed.*knowledge graph', r'ontology.*neural', r'neural.*ontology',
    r'ontology.*transform', r'transform.*ontology', r'ontology.*bert', r'bert.*ontology',
    r'ontology.*embed', r'embed.*ontolog', r'knowledge.*guid.*neural', r'graph neural.*ontolog',
    r'knowledge.*enrich.*match', r'knowledge.*enhanc.*match', r'knowledge.*constrain.*neural',
    r'rule.*guid.*embed', r'logic.*guid.*learn', r'logic.*tensor',
]
I3 = [
    r'explainab', r'interpretab', r'human.?in.?the.?loop', r'\bhitl\b', r'justificat',
    r'reasoning trace', r'proof.*match', r'transparen.*match', r'transparen.*align',
    r'explain.*match', r'explain.*align', r'interpret.*match', r'interpret.*align',
    r'interactive.*feedback', r'user.*feedback.*match',
]
E1_STRONG = [
    r'reinforcement learn', r'deep reinforcement', r'drug discover', r'drug target',
    r'molecule.*property', r'protein.*fold', r'protein.*function', r'autonomous driv',
    r'self.?driving', r'game.*play', r'game.*agent', r'\batari\b', r'medical.*imag.*segment',
    r'tumor.*segment', r'fault.*diagnos(?!.*match)', r'anomaly.*detect(?!.*match)',
    r'speech.*recogn', r'voice.*recogn', r'cyber.*securit(?!.*match)', r'intrusion.*detect',
    r'code.*generat', r'program.*synth', r'style.*transfer', r'image.*generat',
    r'text.*generat(?!.*match)(?!.*align)', r'machine.*translat(?!.*match)',
    r'question.*answer(?!.*match)', r'visual.*question.*answer', r'sentiment.*analy(?!.*match)',
    r'fake.*news', r'misinformat', r'power.*grid(?!.*match)', r'smart.*grid(?!.*match)',
    r'traffic.*flow', r'energy.*forecast',
]
E1_WEAK = [
    r'link.*predict(?!.*match)(?!.*align)', r'knowledge graph.*complet', r'triple.*classif',
    r'relation.*classif(?!.*match)', r'node.*classif', r'graph.*classif', r'text.*classif(?!.*match)',
    r'named.*entity.*recogn', r'recommendat(?!.*match)', r'retriev(?!.*match)(?!.*align)',
    r'summar(?!.*match)', r'translat(?!.*match)', r'predict(?!.*match)(?!.*align)(?!.*harmoniz)',
]
E2 = [
    r'image.*recogn', r'image.*classif', r'image.*retriev', r'video.*classif', r'video.*recogn',
    r'audio.*classif', r'speech.*classif', r'point.*cloud', r'\blidar\b', r'\bradar\b', r'\becg\b',
    r'\beeg\b', r'biosignal', r'image.*segment(?!.*text)(?!.*semantic)', r'visual.*ground(?!.*match)',
    r'scene.*graph(?!.*match)(?!.*align)',
]
E5_DOC_TYPES = [
    r'thesis', r'dissertation', r'report(?!.*technical)', r'poster', r'abstract.*only', r'editorial',
    r'letter.*editor', r'preface', r'foreword', r'chapter', r'book.*review',
]
SURVEY_TITLE = [
    r'\bsurvey\b', r'\breview\b', r'state.?of.?the.?art', r'systematic.*review', r'literature.*review',
    r'comprehensive.*overview', r'taxonomy.*of', r'benchmark.*of', r'comparison.*of.*method',
]
WEIGHTS = {'i2_strong': 2, 'i2_weak': 1, 'i4_strong': 2, 'i4_weak': 1, 'i3': 1,
           'e1_strong': -3, 'e1_weak': -1, 'e2': -2}
CONFIDENCE_INCLUDE = {'high': 5, 'medium': 3}
CONFIDENCE_UNCERTAIN = {'high': 3, 'medium': 2}
DEFAULT_THRESHOLD = 40


def relevance_scores(df, thesaurus):
    df = df.copy()
    abstract = df["abstract"].fillna("").astype(str).str.strip()
    df["has_abstract"] = ~abstract.isin(["", "nan", "NaN", "None"])
    for col in ["title", "abstract", "keywords"]:
        df[col + "_norm"] = df[col].fillna("").astype(str).apply(thesaurus)
    text = (df["title_norm"] + " " + df["title_norm"] + " " + df["abstract_norm"] + " "
            + df["keywords_norm"]).str.strip()
    vectorizer = TfidfVectorizer(max_features=15000, ngram_range=(1, 2), stop_words="english", min_df=1)
    matrix = vectorizer.fit_transform(text.tolist() + [thesaurus(QUERY)])
    scores = cosine_similarity(matrix[:-1], matrix[-1]).flatten()
    df["relevance_score"] = scores
    lo, hi = scores.min(), scores.max()
    df["relevance_score_pct"] = ((scores - lo) / (hi - lo) * 100).round(1) if hi > lo else 50.0
    return df


def _hits(text, patterns):
    return [p for p in patterns if re.search(p, text, re.IGNORECASE)]


def _text(row):
    title = str(row["title_norm"]).lower()
    return f"{title} {title} {str(row['abstract_norm']).lower()} {str(row['keywords_norm']).lower()}"


def adaptive_threshold(df):
    """25th percentile of the relevance score among records with an I2 or I4 signal."""
    signal = df.apply(lambda r: bool(_hits(_text(r), I2_STRONG + I2_WEAK + I4_STRONG + I4_WEAK)), axis=1)
    scores = df.loc[signal, "relevance_score_pct"]
    return DEFAULT_THRESHOLD if len(scores) < 5 else float(scores.quantile(0.25))


def _confidence(score, thresholds):
    return "high" if score >= thresholds["high"] else "medium" if score >= thresholds["medium"] else "low"


def suggest(row, threshold):
    """Return (suggestion, criterion, confidence, signal score)."""
    text, title = _text(row), str(row["title_norm"]).lower()
    i2s, i2w = _hits(text, I2_STRONG), _hits(text, I2_WEAK)
    i4s, i4w = _hits(text, I4_STRONG), _hits(text, I4_WEAK)
    i3 = _hits(text, I3)
    e1s, e1w, e2 = _hits(text, E1_STRONG), _hits(text, E1_WEAK), _hits(text, E2)
    raw = (len(i2s) * WEIGHTS["i2_strong"] + len(i2w) * WEIGHTS["i2_weak"] + len(i4s) * WEIGHTS["i4_strong"]
           + len(i4w) * WEIGHTS["i4_weak"] + len(i3) * WEIGHTS["i3"] + len(e1s) * WEIGHTS["e1_strong"]
           + len(e1w) * WEIGHTS["e1_weak"] + len(e2) * WEIGHTS["e2"])
    score = max(0, min(10, raw))
    has_abstract = bool(row["has_abstract"])

    try:
        if not 2020 <= int(float(row["year"])) <= 2025:
            return "exclude", "E6", "high", score
    except (TypeError, ValueError):
        pass
    if _hits(title + " " + str(row["doc_type"]).lower(), E5_DOC_TYPES):
        return "exclude", "E5", "high", score
    if _hits(title, SURVEY_TITLE) and not i2s:
        return "survey", "E5 survey", "high", score
    if e2 and not i2s:
        return "exclude", "E2", "medium", score
    if e1s and not i2s:
        return ("uncertain", "E1? no abstract", "low", score) if not has_abstract else ("exclude", "E1", "high", score)
    if len(e1w) >= 2 and not i2s and not i2w and not i4s:
        return ("uncertain", "E1? no abstract", "low", score) if not has_abstract else ("exclude", "E1", "medium", score)
    if i2s and (i4s or i4w):
        return "include", "I2+I4", _confidence(score, CONFIDENCE_INCLUDE), score
    if i2s:
        return "uncertain", "I2 only", _confidence(score, CONFIDENCE_UNCERTAIN), score
    if i4s and i2w:
        return "uncertain", "I4 + weak I2", _confidence(score, CONFIDENCE_UNCERTAIN), score
    if i4w and i2w:
        return "uncertain", "weak I4 + weak I2", _confidence(score, CONFIDENCE_UNCERTAIN), score
    if i3 and not e1s:
        return "uncertain", "I3 only", _confidence(score, CONFIDENCE_UNCERTAIN), score
    if i4s or i4w:
        return "uncertain", "I4 only", _confidence(score, CONFIDENCE_UNCERTAIN), score
    if i2w:
        return "uncertain", "weak I2 only", _confidence(score, CONFIDENCE_UNCERTAIN), score
    if float(row["relevance_score_pct"]) >= threshold:
        return "uncertain", "high relevance score", "low", score
    if not has_abstract:
        return "uncertain", "no abstract", "low", score
    return "exclude", "E1", "low", score


def prioritise(df, thesaurus):
    df = relevance_scores(df, thesaurus)
    threshold = adaptive_threshold(df)
    out = df.apply(lambda r: suggest(r, threshold), axis=1, result_type="expand")
    df[["suggestion", "suggestion_criterion", "suggestion_confidence", "signal_score"]] = out
    df = df.sort_values("relevance_score", ascending=False)
    keep = ["title", "year", "doi", "database", "query", "relevance_score_pct", "suggestion",
            "suggestion_criterion", "suggestion_confidence", "signal_score"]
    return df[keep], threshold


if __name__ == "__main__":
    thesaurus = Thesaurus(VOSVIEWER / "thesaurus_identified.txt")
    primary = pd.read_csv(INTERIM / "primary_records.csv", encoding="utf-8-sig", dtype=str)
    complementary = pd.read_csv(INTERIM / "complementary_records.csv", encoding="utf-8-sig", dtype=str)

    p, t1 = prioritise(primary, thesaurus)
    p.to_csv(INTERIM / "prioritised_primary.csv", index=False, encoding="utf-8-sig")
    print(f"primary wave ({len(p)} records), adaptive threshold {t1:.1f}")
    print(p["suggestion"].value_counts().to_string(), "\n")

    both, t2 = prioritise(pd.concat([primary, complementary], ignore_index=True), thesaurus)
    both.to_csv(INTERIM / "prioritised_all.csv", index=False, encoding="utf-8-sig")
    r4 = both[both["query"] == "R4"]
    print(f"primary + R4 scored together ({len(both)} records), adaptive threshold {t2:.1f}")
    print("suggestions for the R4 records:")
    print(r4["suggestion"].value_counts().to_string(), "\n")

    # Compare with the tool output recorded during screening. Scores are not
    # identical across machines (most likely tie ordering at the 15,000-term
    # vocabulary cut-off), so a handful of borderline suggestions can change.
    recorded = pd.read_csv(SCREENING / "records_screened.csv", dtype=str, keep_default_na=False)
    key = lambda d: (d["title"].str.lower().str.strip() + "|" + d["year"].str[:4] + "|"
                     + d["doi"].str.lower().str.strip())
    for wave, rerun in [("primary", p), ("complementary", r4)]:
        rec = recorded[recorded["wave"] == wave]
        merged = rerun.fillna("").assign(k=key(rerun.fillna(""))).merge(
            rec.assign(k=key(rec))[["k", "tool_suggestion"]].drop_duplicates("k"), on="k")
        same = (merged["suggestion"] == merged["tool_suggestion"]).sum()
        print(f"{wave}: {same} of {len(merged)} suggestions identical to those recorded during screening")
