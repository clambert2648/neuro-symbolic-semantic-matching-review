# Data

All files are UTF-8 CSV. Empty cells mean "not applicable" or "not recorded".

## Identifiers

| Pattern | Meaning |
|---|---|
| `001`-`1888` | primary-search record (rank in the frozen screening file of the primary wave) |
| `C001`-`C820` | complementary-search (R4) record, in the order it was screened |
| `R4-01`-`R4-40` | R4 report read in full text |
| `BT..`, `SV..` | citation-searching record (found in the reference list of an article, `BT`, or of a survey, `SV`) |
| `1889` | expert recommendation (FLORA) |

An included study keeps the identifier of the report it came from, e.g. `058` (NeuSymEA),
`R4-36` (ReasonAlign), `BT03` (PRASE). `data/extraction/studies.csv` maps identifiers to
system names and BibTeX keys of the article.

## `screening/`

**`identification_counts.csv`** - counts produced by `scripts/02_deduplicate.py`
(records per database, duplicates removed, records screened).

**`records_screened.csv`** - the 2,708 records screened on title and abstract.
Abstracts are not included (see `raw/README.md`).

| Column | Content |
|---|---|
| `record_id` | see above |
| `wave` | `primary` (R1-R3) or `complementary` (R4) |
| `title`, `authors`, `year`, `doi`, `venue`, `doc_type`, `author_keywords` | as exported by the database(s) |
| `databases` | databases that returned the record, joined by `+` |
| `queries` | queries that returned the record, joined by `+` |
| `tool_score` | relevance score (0-100) shown during screening |
| `tool_suggestion` | rule-based suggestion shown during screening (`include`, `uncertain`, `survey`, `exclude`) |
| `ta_decision` | final title-and-abstract decision: `include` (sent to full text), `exclude`, or `survey` (survey or review, not a primary study; the 59 primary-wave surveys were used for citation searching, the 25 R4 surveys were not) |
| `ta_reason` | exclusion criterion (E1-E6, I4, `duplicate`); not recorded for R4 exclusions |
| `validated_by` | author who validated the final decision (every record, including those reviewed in groups; see `protocol/protocol.md`, section 5) |
| `fulltext_id` | identifier of the full-text report, when sent to full text |

**`citation_searching.csv`** - the 50 citation-searching records and the expert
recommendation, with `found_in` (source survey or article) and the title-and-abstract decision.

**`full_text_assessment.csv`** - one row per report sought in full text (276 rows: 216
primary, 40 complementary, 20 other methods).

| Column | Content |
|---|---|
| `report_id`, `route`, `title`, `year`, `doi` | report and how it was found |
| `outcome` | `included`, `excluded` or `not retrieved` |
| `basis` | recorded reason for the outcome (see below) |
| `detail` | short justification |
| `qa_q1`-`qa_q6`, `qa_total` | quality scores (Yes 1, Partly 0.5, No 0; Q6 not counted) |

Values of `basis` for exclusions. Each excluded report has one, the criterion on which
its exclusion rests under the final criteria (`protocol/protocol.md`, section 3);
`detail` names a second failed criterion where there is one.

| Basis | Meaning |
|---|---|
| `I4-A` | no real neural component or no real symbolic component |
| `I4-B` | symbolic component present but passive (input, verbalised or flattened structure) |
| `I2` | no matching task between distinct sources |
| `I5` | evaluation without a named dataset, a standard matching metric or an external baseline |
| `E3`, `E4`, `E5` | no algorithmic method; no empirical evaluation; document type |
| `full text not in a working language` | full text only in Chinese (five reports) or Portuguese (one) |

Other values of `basis`: `included` marks the main report of each of the 27 studies and
`companion report` an additional report of an included study (two reports; their evidence
is used, they are not separate studies). For reports not retrieved, `basis` gives the
cause: inaccessible, withdrawn, or full text only in Chinese (two reports that could not
be obtained in a readable version).

Quality scores are given for the reports that were scored before their exclusion. No
report is excluded on the quality score alone: the four that scored below 3/5 (`082`,
`115`, `786`, `971`) also fail an eligibility criterion, which is their `basis`.

The reports first excluded under the former I4-strict criterion (175), at the second
author's validation (6) or below the quality threshold (4) were re-assessed against the
final criteria in November 2026 (`protocol/protocol.md`, section 9). No outcome changed.

## `extraction/`

One row per included study (27), in the order of Table A.1 of the article. Codes and
rules: [`protocol/coding_guide.md`](../protocol/coding_guide.md).

| File | Content |
|---|---|
| `studies.csv` | system name, BibTeX key, first author, year of the assessed version, title, DOI or arXiv id, task family, route, venue type at extraction, quality scores |
| `coding.csv` | C1: Kautz type, knowledge-exploitation strategy (dominant, secondary), stage (dominant, secondary, mixed), symbolic function (dominant, all present), the symbolic operation and what produces the final decision, decisive quote and section |
| `explanation_hitl.csv` | C2: explanation mode, artifact, target and evaluation; HITL presence, effect on output, effort reported; supporting evidence |
| `rq2_audit.csv` | negative audit for RQ2: expert feedback loop, explanation user study, human-effort measure, with the evidence for each "no" |
| `context.csv` | C3: task family, domain, multilinguality, languages, benchmarks, heterogeneity types, external knowledge source (D2), code and data availability |
| `ablation.csv` | evaluation practices: ablation reported, what is varied, whether a control switches off the dominant symbolic operation |

Two studies reinstated after the I4 revision had their scores reset to 0 at the earlier
exclusion. SLHCat (`828`) keeps the scores it received before that exclusion (4/5; Q6 was
not recorded). LogMap + LLM oracles (`282`) kept no earlier scores and was scored from the
full text after its reinstatement (4.5/5).
