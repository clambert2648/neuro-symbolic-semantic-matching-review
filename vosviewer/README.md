# VOSviewer maps

Author-keyword co-occurrence maps of the article (VOSviewer 1.6.20).

| Article figure | Corpus | Input | Thesaurus | Minimum occurrences | Saved map |
|---|---|---|---|---|---|
| `fig:vos-network`, `fig:vos-overlay` | 2,708 identified records | `identified_records.ris` | `thesaurus_identified.txt` | 5 (160 keywords, 12 clusters) | `map_identified.json`, `map_identified.txt`, `network_identified.txt` |
| `fig:vos-included` | 27 included studies | `included_studies.ris` | `thesaurus_included.txt` | 2 (11 keywords, 4 clusters; unconnected items kept) | `map_included.json` |

Settings in both cases: *Create a map based on bibliographic data* > *Read data from
reference manager files* (RIS) > *Co-occurrence* > *Author keywords* > *Full counting*,
then the thesaurus file. All keywords above the threshold are kept. The overlay colours
items by average publication year.

- `identified_records.ris` is written by `scripts/04_bibliometrics.py` from
  `data/screening/records_screened.csv` (author keywords only).
- `included_studies.ris` was exported from the reference manager. Ten of the 27 studies
  have no author keywords; none were added. The 81 keywords of the other 17 were checked
  against the PDFs.
- `thesaurus_included.txt` is the identified-corpus thesaurus plus a few rules for
  variants that only occur in the included studies (e.g. "vector embeddings" to "embedding").

The twelve clusters of `map_identified.json` are grouped into the five macro-themes of
the thematic-composition figure in `scripts/05_thematic_delta.py`.

The same thesaurus (`thesaurus_identified.txt`) also normalises terminology before the
relevance scoring of `scripts/03_prioritize_screening.py`.
