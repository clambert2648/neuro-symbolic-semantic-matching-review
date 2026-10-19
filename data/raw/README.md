# Raw database exports

The exports downloaded from each database, unchanged. They are the input of
`scripts/02_deduplicate.py`, which rebuilds every identification count of the PRISMA flow diagram.

```
scopus/  R1_scopus.csv  R2A_scopus.csv  R2B_scopus.csv  R3_scopus.csv  R4_scopus.csv
ieee/    R1_ieee.csv    R2A_ieee.csv    R2B_ieee.csv    R3_ieee.csv    R4_ieee.csv
acm/     R1_acm.bib     R2A_acm.bib     R2B_acm.bib     R3_acm.bib     R4_acm.bib
arxiv/   R1_arxiv.csv   R2A_arxiv.csv   R2B_arxiv.csv   R3_arxiv.csv   R4_arxiv.csv
citation_searching_abstracts.csv
```

R1-R3 were exported on 27 February 2026 and R4 on 14 July 2026, with the strings and
filters in [`protocol/search_strings.md`](../../protocol/search_strings.md).
`citation_searching_abstracts.csv` holds the titles, abstracts and keywords of the
citation-searching records (used by `scripts/05_thematic_delta.py`).

**These files are not in the public repository.** The exports contain abstracts and
metadata that Scopus, IEEE Xplore and ACM license for individual use, not for
redistribution. The public repository keeps every record without its abstract in
`data/screening/records_screened.csv`, which is enough to check every screening decision
and to rerun `04_bibliometrics.py` and `06_results.py`. Steps 02, 03 and 05 need the
exports: re-export them with the documented strings, or ask the corresponding author.
