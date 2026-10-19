"""Retrieve arXiv records through the arXiv API (Section 3.1).

Scopus, IEEE Xplore and ACM were exported manually from their web interfaces;
arXiv was queried with this script. The API returns results ranked at query
time, so a new run will not return exactly the records in data/raw/arxiv/.
The files used in the review are kept as retrieved (primary: 27 Feb 2026,
complementary R4: 14 Jul 2026).

Usage:
    python scripts/01_fetch_arxiv.py primary
    python scripts/01_fetch_arxiv.py complementary
"""

import sys
import time

import arxiv
import pandas as pd

from common import RAW

PRIMARY = {
    "R1": '(abs:"schema matching" OR abs:"ontology alignment" OR abs:"data harmonization" '
          'OR abs:"semantic integration") AND (abs:"knowledge graph" OR abs:"ontology" '
          'OR abs:embedding OR abs:transformer OR abs:"language model")',
    "R2A": '(abs:"neuro-symbolic" OR abs:neurosymbolic OR abs:"neural-symbolic") AND '
           '(abs:"knowledge graph" OR abs:ontology) AND (abs:matching OR abs:alignment OR abs:explainab)',
    "R2B": '(ti:hybrid OR ti:integration OR ti:fusion) AND (abs:"knowledge graph" OR abs:ontology) '
           'AND (abs:"neural network" OR abs:transformer OR abs:embedding) AND (abs:matching OR abs:alignment)',
    "R3": '(abs:"data harmonization" OR abs:"semantic matching" OR abs:"variable mapping") AND '
          '(abs:"monitoring and evaluation" OR abs:multilingual OR abs:"international development") '
          'AND (abs:"machine learning" OR abs:NLP OR abs:transformer)',
}

# R4: a single query combining the reasoning terms returns nothing on the API,
# so each reasoning term is run as its own sub-query and results are merged.
REASONING = ['"description logic"', '"logical reasoning"', '"symbolic reasoning"',
             '"fuzzy logic"', '"probabilistic reasoning"', '"non-axiomatic logic"',
             '"formal concept analysis"', "reasoner"]
NEURAL = ('(abs:"neural network" OR abs:"deep learning" OR abs:embedding OR abs:transformer '
          'OR abs:"language model" OR abs:BERT OR abs:"graph neural network" OR abs:GNN)')
TASK = ('(abs:matching OR abs:alignment OR abs:"entity resolution" OR abs:"entity alignment" '
        'OR abs:"schema matching" OR abs:"ontology alignment" OR abs:"ontology matching")')


def record(result, query):
    return {
        "title": result.title.replace("\n", " "),
        "abstract": result.summary.replace("\n", " "),
        "authors": "; ".join(str(a) for a in result.authors),
        "year": result.published.year,
        "doi": result.doi or "",
        "source": "arXiv:" + result.entry_id.split("/")[-1],
        "keywords": "",
        "doc_type": "Preprint",
        "citations": "",
        "database": "ArXiv",
        "query": query,
    }


def fetch_primary():
    client = arxiv.Client()
    for qid, query in PRIMARY.items():
        search = arxiv.Search(query=query, max_results=200, sort_by=arxiv.SortCriterion.Relevance)
        rows = []
        for r in client.results(search):
            if 2020 <= r.published.year <= 2025:
                rows.append(record(r, qid))
            time.sleep(0.1)
        pd.DataFrame(rows).to_csv(RAW / "arxiv" / f"{qid}_arxiv.csv", index=False, encoding="utf-8-sig")
        print(f"{qid}: {len(rows)} records")


def fetch_complementary():
    client = arxiv.Client(page_size=100, delay_seconds=3, num_retries=3)
    seen = {}
    for term in REASONING:
        search = arxiv.Search(query=f"abs:{term} AND {NEURAL} AND {TASK}", max_results=500,
                              sort_by=arxiv.SortCriterion.SubmittedDate)
        for r in client.results(search):
            if not 2020 <= r.published.year <= 2025:
                continue
            arxiv_id = r.entry_id.split("/")[-1].rsplit("v", 1)[0]   # drop the version suffix
            if arxiv_id in seen:
                seen[arxiv_id]["query"] += f";{term}"
            else:
                seen[arxiv_id] = record(r, "R4:" + term)
    pd.DataFrame(list(seen.values())).to_csv(RAW / "arxiv" / "R4_arxiv.csv", index=False, encoding="utf-8-sig")
    print(f"R4: {len(seen)} unique records")


if __name__ == "__main__":
    wave = sys.argv[1] if len(sys.argv) > 1 else "primary"
    if wave not in ("primary", "complementary"):
        sys.exit("usage: python scripts/01_fetch_arxiv.py [primary|complementary]")
    (RAW / "arxiv").mkdir(parents=True, exist_ok=True)
    fetch_primary() if wave == "primary" else fetch_complementary()
