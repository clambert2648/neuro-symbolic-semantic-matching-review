"""Shared helpers: paths, export loaders, deduplication and text normalisation."""

import re
from pathlib import Path

import pandas as pd
from rapidfuzz import fuzz

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
INTERIM = ROOT / "data" / "interim"          # regenerated, not versioned
SCREENING = ROOT / "data" / "screening"
EXTRACTION = ROOT / "data" / "extraction"
VOSVIEWER = ROOT / "vosviewer"
FIGURES = ROOT / "figures"
RESULTS = ROOT / "results"

PRIMARY_QUERIES = ["R1", "R2A", "R2B", "R3"]
DATABASES = ["Scopus", "IEEE", "ACM", "ArXiv"]
COLUMNS = ["title", "abstract", "authors", "year", "doi", "source", "keywords",
           "doc_type", "citations", "database", "query"]
FUZZY_THRESHOLD = 95


def title_score(a: str, b: str) -> int:
    """Title similarity on a 0-100 integer scale (Indel ratio, rounded)."""
    return int(round(fuzz.ratio(a, b)))


# --------------------------------------------------------------------------
# Loaders: one function per database, all returning the same columns
# --------------------------------------------------------------------------

def _col(df, name):
    return df.get(name, pd.Series([""] * len(df), dtype=str)).fillna("").astype(str)


def load_scopus(path, query):
    df = pd.read_csv(path, encoding="utf-8-sig", dtype=str)
    return pd.DataFrame({
        "title": _col(df, "Title").str.strip(),
        "abstract": _col(df, "Abstract"),
        "authors": _col(df, "Authors"),
        "year": _col(df, "Year"),
        "doi": _col(df, "DOI").str.lower().str.strip(),
        "source": _col(df, "Source title"),
        "keywords": _col(df, "Author Keywords"),
        "doc_type": _col(df, "Document Type"),
        "citations": _col(df, "Cited by"),
        "database": "Scopus",
        "query": query,
    })


def load_ieee(path, query):
    df = pd.read_csv(path, encoding="utf-8-sig", dtype=str)
    return pd.DataFrame({
        "title": _col(df, "Document Title").str.strip(),
        "abstract": _col(df, "Abstract"),
        "authors": _col(df, "Authors"),
        "year": _col(df, "Publication Year"),
        "doi": _col(df, "DOI").str.lower().str.strip(),
        "source": _col(df, "Publication Title"),
        "keywords": _col(df, "Author Keywords"),
        "doc_type": _col(df, "Document Identifier"),
        "citations": _col(df, "Article Citation Count"),
        "database": "IEEE",
        "query": query,
    })


def load_arxiv(path, query):
    """arXiv files are written by 01_fetch_arxiv.py in the common format."""
    df = pd.read_csv(path, encoding="utf-8-sig", dtype=str)
    out = pd.DataFrame({c: _col(df, c) for c in COLUMNS})
    out["title"] = out["title"].str.strip()
    out["doi"] = out["doi"].str.lower().str.strip()
    out["doc_type"] = out["doc_type"].replace("", "Preprint")
    out["database"] = "ArXiv"
    out["query"] = query
    return out


def _bib_field(entry, field):
    m = re.search(rf'{field}\s*=\s*[{{"](.+?)[}}"]\s*[,}}]', entry, re.IGNORECASE | re.DOTALL)
    if not m:
        return ""
    value = re.sub(r"[{}]", "", m.group(1).strip())
    return re.sub(r"\s+", " ", value)


def _bib_abstract(entry):
    m = re.search(r"abstract\s*=\s*\{(.*?)\}\s*[,\n]", entry, re.IGNORECASE | re.DOTALL)
    return re.sub(r"\s+", " ", m.group(1).strip()) if m else ""


def load_acm(path, query):
    """ACM BibTeX export. Book chapters (@inbook) are dropped (criterion E5)."""
    content = Path(path).read_text(encoding="utf-8")
    entries = [e.strip() for e in re.split(r"\n(?=@)", content) if e.strip()]
    records = []
    for entry in entries:
        m = re.match(r"@(\w+)\s*\{", entry)
        if not m or m.group(1).lower() == "inbook":
            continue
        kind = m.group(1).lower()
        records.append({
            "title": _bib_field(entry, "title"),
            "abstract": _bib_abstract(entry),
            "authors": _bib_field(entry, "author"),
            "year": _bib_field(entry, "year"),
            "doi": _bib_field(entry, "doi").lower().strip(),
            "source": _bib_field(entry, "booktitle") or _bib_field(entry, "journal"),
            "keywords": _bib_field(entry, "keywords"),
            "doc_type": "Conference Paper" if kind == "inproceedings" else "Journal Article",
            "citations": "",
            "database": "ACM",
            "query": query,
        })
    return pd.DataFrame(records, columns=COLUMNS)


LOADERS = {
    "scopus": (load_scopus, "csv"),
    "ieee": (load_ieee, "csv"),
    "acm": (load_acm, "bib"),
    "arxiv": (load_arxiv, "csv"),
}


def load_export(db, query):
    loader, ext = LOADERS[db]
    path = RAW / db / f"{query}_{db}.{ext}"
    if not path.exists():
        raise SystemExit(f"Missing {path.relative_to(ROOT)}: the raw database exports are not "
                         "distributed with this repository (see data/raw/README.md).")
    return loader(path, query)


# --------------------------------------------------------------------------
# Deduplication
# --------------------------------------------------------------------------

def _merge_labels(a, b, order):
    parts = set(str(a).split("+")) | set(str(b).split("+"))
    return "+".join(x for x in order if x in parts)


def deduplicate(df, merge_col, merge_order, fuzzy_on="no_doi", threshold=FUZZY_THRESHOLD):
    """Two-pass deduplication.

    Pass 1: exact DOI match. Pass 2: title similarity >= threshold with the
    same publication year (or a missing year). The labels in `merge_col`
    (query or database) of a removed duplicate are merged into the kept record.

    fuzzy_on="no_doi" compares only records without a DOI (primary search);
    fuzzy_on="all" compares every record left after pass 1 (complementary search).
    Returns (deduplicated frame, number removed by DOI, number removed by title).
    """
    df = df.copy().reset_index(drop=True)
    title = df["title"].fillna("").str.lower().str.strip()
    doi = df["doi"].fillna("").str.lower().str.strip()
    drop, labels = set(), {}

    for _, group in df[doi != ""].groupby(doi[doi != ""]):
        keep = group.index[0]
        for dup in group.index[1:]:
            labels[keep] = _merge_labels(labels.get(keep, df.at[keep, merge_col]),
                                         df.at[dup, merge_col], merge_order)
            drop.add(dup)
    n_doi = len(drop)

    mask = ~df.index.isin(drop)
    if fuzzy_on == "no_doi":
        mask &= (doi == "")
    idx = list(df.index[mask])
    years = df["year"].astype(str)
    n_title = 0
    for a_pos, i in enumerate(idx):
        if i in drop:
            continue
        for j in idx[a_pos + 1:]:
            if j in drop:
                continue
            same_year = years[i] == years[j] or "nan" in (years[i], years[j])
            if same_year and title_score(title[i], title[j]) >= threshold:
                labels[i] = _merge_labels(labels.get(i, df.at[i, merge_col]),
                                          df.at[j, merge_col], merge_order)
                drop.add(j)
                n_title += 1

    for i, value in labels.items():
        df.at[i, merge_col] = value
    return df[~df.index.isin(drop)].reset_index(drop=True), n_doi, n_title


def canonical_title(t):
    """Lower case, expand KG/KGs, drop punctuation. Used against already-screened records."""
    t = str(t).lower().strip()
    t = re.sub(r"\bkgs\b", "knowledge graphs", t)
    t = re.sub(r"\bkg\b", "knowledge graph", t)
    t = re.sub(r"[^a-z0-9 ]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


# --------------------------------------------------------------------------
# Terminology normalisation (VOSviewer thesaurus, single pass)
# --------------------------------------------------------------------------

class Thesaurus:
    """Applies all label -> replacement rules of a VOSviewer thesaurus in one pass,
    longest labels first, so replacements never cascade."""

    def __init__(self, path):
        self.mapping = {}
        with open(path, encoding="utf-8") as f:
            next(f)  # header: label<TAB>replace by
            for line in f:
                parts = line.strip().split("\t", 1)
                if len(parts) == 2 and parts[0].strip() and parts[1].strip():
                    self.mapping[parts[0].strip().lower()] = parts[1].strip().lower()
        labels = sorted(self.mapping, key=len, reverse=True)
        self.pattern = re.compile("|".join(r"\b" + re.escape(x) + r"\b" for x in labels),
                                  re.IGNORECASE)

    def __call__(self, text):
        text = str(text or "").lower()
        return self.pattern.sub(lambda m: self.mapping.get(m.group(0).lower(), m.group(0)), text)
