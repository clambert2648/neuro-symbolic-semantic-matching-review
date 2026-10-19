# Neuro-symbolic semantic matching: systematic review data and code

Data, code and documentation for the article

> Lambert-Tremblay, C. and Tajeuna, E. G. *Neuro-Symbolic Semantic Matching of
> Heterogeneous Data: A Systematic Review of Emerging Architectures, Explainability, and
> Human Validation.* Manuscript under review.

The review follows PRISMA 2020. It screened 2,708 records from Scopus, IEEE Xplore,
ACM Digital Library and arXiv (2020-2025), added citation searching, and analysed
27 primary studies. This repository holds the search strings, the screening decisions,
the full-text assessments, the coded extraction, the coding guide, and the scripts that
rebuild the counts, tables and figures of the article. The raw database exports are
the only input kept out of it (publisher licences).

## Contents

```
protocol/
  protocol.md              criteria, quality grid, selection process, amendments
  search_strings.md        all queries as run, with dates, filters and counts
  coding_guide.md          how each study was coded (stage, function, Kautz, ...)
data/
  screening/               records screened, citation searching, full-text assessment
  extraction/              coded data of the 27 included studies
  raw/                     database exports (local only, see data/raw/README.md)
scripts/                   01-06, run in order
vosviewer/                 keyword-map inputs, thesauri and saved maps
figures/                   figures of the article (the PRISMA diagram is drawn in the manuscript)
results/                   tables and checks written by the scripts
```

Column definitions: [data/README.md](data/README.md).

## From the article to this repository

| Article | Files | Script |
|---|---|---|
| Search strategy (Table 1) | `protocol/search_strings.md` | `01_fetch_arxiv.py` (arXiv only) |
| Eligibility criteria and quality checklist (Tables 2-3) | `protocol/protocol.md` | - |
| Extraction and coding, coding framework (Table 4) | `protocol/coding_guide.md` (replaces the former coding appendix) | - |
| PRISMA flow diagram (`fig:prisma`) | `data/screening/*.csv` | `02_deduplicate.py`, `06_results.py` -> `results/prisma_flow.csv` |
| Title-and-abstract screening support | `data/screening/records_screened.csv` (`tool_*` columns) | `03_prioritize_screening.py` |
| Label-inflation patterns (Table 5) | `data/screening/full_text_assessment.csv` (`basis`, `detail`) | - |
| Cross-database overlap (supplementary) | `results/cross_database_overlap.csv` | `04_bibliometrics.py` |
| Keyword maps (`fig:vos-network`, `fig:vos-overlay`, `fig:vos-included`) | `vosviewer/` | `04_bibliometrics.py` + VOSviewer |
| Thematic composition (`fig:thematic-delta`) | `results/thematic_delta.csv` | `05_thematic_delta.py` |
| Included studies by year (`fig:included-years`) | `data/extraction/studies.csv` | `04_bibliometrics.py` |
| Evidence map (`fig:evidence-map`) | `data/extraction/` | `06_results.py` |
| RQ1 counts, stage by function (Table 6) | `data/extraction/coding.csv`, `ablation.csv` | `06_results.py` |
| RQ2 counts | `data/extraction/explanation_hitl.csv`, `rq2_audit.csv` | `06_results.py` |
| RQ3 counts | `data/extraction/context.csv` | `06_results.py` |
| Included studies (Table A.1) | `data/extraction/studies.csv`, `coding.csv` | `06_results.py` |
| Analytical framework (`fig:framework`) | `figures/analytical_framework.tex` | - |

## Reproducing the results

Python 3.10 or later.

```bash
pip install -r requirements.txt

python scripts/04_bibliometrics.py    # figure of included studies by year, overlap table, RIS for VOSviewer
python scripts/06_results.py          # every count of the article, Table 6, Table A.1, evidence map
```

`06_results.py` recomputes the counts reported in the text, the flow diagram, Table 6 and
Table A.1 from the data files and writes the comparison to `results/article_checks.csv`
(109 values, all reproduced). Reasons for full-text exclusions are recorded per report in
`data/screening/full_text_assessment.csv` and tallied in `results/fulltext_exclusions.csv`.

The three other steps need the raw database exports in `data/raw/`, which are not
public (publisher licences; see [data/raw/README.md](data/raw/README.md)):

```bash
python scripts/02_deduplicate.py         # 3,224 records -> 2,708 screened (identification counts)
python scripts/03_prioritize_screening.py
python scripts/05_thematic_delta.py      # thematic composition figure
```

`02_deduplicate.py` reproduces the identification counts and the screened records
exactly. `03_prioritize_screening.py` re-runs the screening support tools. Their relevance
scores are not identical across machines (the difference persists with the same library
versions and input text, most likely from how ties at the 15,000-term vocabulary cut-off
are ordered), so a few borderline suggestions change: 3 of 2,708 in our check. The
suggestions actually shown during screening are kept in `records_screened.csv`.

`01_fetch_arxiv.py` documents the arXiv queries. The API ranks results at query time, so
a new run does not return exactly the archived records.

Figures made outside Python: the keyword maps (VOSviewer, settings in
[vosviewer/README.md](vosviewer/README.md)) and the framework diagram (TikZ, compile
`figures/analytical_framework.tex` with `pdflatex`).

## Not included

Full texts of the studies (copyright), the raw database exports (licences), and the
working files of the review (screening interface, intermediate workbooks, earlier
versions of the corpus). The full decision log, in French, is available from the
corresponding author.

## Licence

Code: MIT ([LICENSE](LICENSE)). Data and documentation: CC BY 4.0.

## Citation

See [CITATION.cff](CITATION.cff). Contact: Constance Lambert-Tremblay, Université du
Québec en Outaouais (lamc44@uqo.ca).
