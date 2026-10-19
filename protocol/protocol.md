# Review protocol

Condensed English version of the protocol followed for the review, including every
amendment made after screening started. The protocol was written before screening and
versioned with the review materials; it was not registered. Section numbers refer to the
article.

## 1. Questions

- **RQ1 - Architectures and evaluation.** Which explicit or hybrid neuro-symbolic
  architectures have been proposed for semantic and structural matching of heterogeneous
  data, how do they combine neural and symbolic components, and how are they evaluated?
- **RQ2 - Explainability and interactive validation.** How do these approaches
  operationalise explainability and human-in-the-loop (HITL) validation, including
  reasoning traces, expert feedback, and trade-offs between performance and interpretability?
- **RQ3 - Application contexts.** In which domains, linguistic settings and heterogeneity
  conditions have these approaches been applied, and what design implications follow for
  explainable semantic matching in knowledge-intensive environments?

The review follows PRISMA 2020 (Page et al., 2021) and the computer-science procedure of
Carrera-Rivera et al. (2022).

## 2. Sources and search (Section 3.1)

Scopus, IEEE Xplore, ACM Digital Library (Full-Text Collection) and arXiv, publications
2020-2025. Four primary queries were built from the PICOC: R1 (semantic matching and
NLP/KG), R2A (explicit neuro-symbolic), R2B (implicit neural-symbolic hybrid, integration
terms restricted to the title after pilot testing), R3 (monitoring-and-evaluation and
multilingual context). The R2A/R2B split was kept because the two queries overlapped by
only 2.3 % in pilot runs. Full strings, filters and counts: [search_strings.md](search_strings.md).

Records were merged with exact DOI matching, then title similarity of at least 95 % with
the same publication year ([`scripts/02_deduplicate.py`](../scripts/02_deduplicate.py)).

## 3. Eligibility criteria (Section 3.2, Table 2)

The protocol states the inclusion rule as **(I2 or I3) and I4 and I5**, with I1 and I6 as
formal conditions; any exclusion criterion is sufficient to exclude. Because E1 excludes
studies without an inter-source matching output, I3 never admitted a study on its own:
every included study has an eligible matching task (I2).

| ID | Criterion |
|---|---|
| I1 | Journal article or conference paper published 2020-2025. arXiv preprints admitted under an explicit exception, with their status recorded. |
| I2 | Matching, alignment, mapping, repair, revision or harmonisation between distinct heterogeneous sources. |
| I3 | Explicit explanation, interpretability or HITL treatment tied to matching decisions. |
| I4 | An authentic neural component and an authentic symbolic component, and the symbolic component participates in the matcher rather than serving only as passive structured input. |
| I5 | At least one named dataset, a standard matching metric (F1, precision, recall, MRR, Hits@k) and at least one external baseline on the same task. |
| I6 | Full text accessible. |
| E1 | No inter-source matching task (stand-alone KG completion, link prediction, classification, question answering, recommendation). Inter-KG entity alignment remains eligible. |
| E2 | Image, video, audio or signal matching without a textual or semantic component. |
| E3 | No algorithmic method. |
| E4 | No empirical evaluation. |
| E5 | Thesis, report, chapter, editorial, poster or patent. Surveys are kept for citation searching only. |
| E6 | Outside 2020-2025 or no exploitable abstract. |

For I5, OAEI campaign results count as an external comparison, since they rank the system
against the other participants on the same task. Evidence from all reports of a study
(companion reports) is used.

**Operational definition of I4.** Condition A: the system has a real neural component
(neural network, embeddings, GNN, transformer, LLM) **and** a real symbolic component
(logical reasoning, axioms, description logic, probabilistic or fuzzy inference, executed
formal constraints, logic rules, formal concept analysis). Condition B: the symbolic
component executes an operation that participates in matching (training, preprocessing or
inference) and is not merely input data. Failing A gives exclusion code I4-A; failing B
(passive or verbalised structure, N0) gives I4-B. The stage at which the operation acts is
not an eligibility criterion; it is coded afterwards ([coding_guide.md](coding_guide.md)).
I4 was assessed from the architecture section of the full text, never from the abstract.
At title-and-abstract screening, I4 was applied broadly: any mention of a neural plus
symbolic combination sent the record to full text.

## 4. Quality assessment (Table 3)

Each report passing I4 was scored on Q1-Q5 (Yes = 1, Partly = 0.5, No = 0); retention
threshold 3/5. Q6 is recorded but not scored.

| Item | Question |
|---|---|
| Q1 | Are the objectives and the matching or harmonisation task clearly defined? |
| Q2 | Is the neural-symbolic architecture described in enough detail to be reimplemented? (reproducibility of the description, not I4) |
| Q3 | Is a named dataset with size information and at least one standard metric reported? (undisclosed proprietary data = Partly) |
| Q4 | Are matching explanations, structured justifications or HITL mechanisms reported? (scores only = Partly) |
| Q5 | Is at least one external baseline evaluated on the same dataset or task? (internal ablation only = Partly) |
| Q6 | Bonus, not scored: are limitations or threats to validity discussed? |

## 5. Selection process

1. **Title and abstract** (one reviewer, the first author). Aim: high recall; when in
   doubt, the record goes to full text. Two tools ordered the records and suggested a label
   (TF-IDF relevance to a query written from the research questions; keyword rules aligned
   with I2, I3, I4, E1, E2, E5, E6) - see
   [`scripts/03_prioritize_screening.py`](../scripts/03_prioritize_screening.py).
   The tools' dictionaries, weights and thresholds were fixed before screening. Records were
   read in descending order of relevance. In the primary wave, records on which the tools
   agreed were reviewed in groups:
   - 119 records with a high-confidence "include" suggestion; 36 of them were excluded when
     read;
   - 1,075 records whose relevance score, rule suggestion and signal score all pointed to
     exclusion (signal score <= 2 and relevance <= 15 %, or signal score <= 1), also checked
     with targeted keyword searches for matching vocabulary hidden in the abstract. This
     group was defined during screening, once reading in relevance order had stopped
     producing inclusions.

   The tools only suggested; the first author validated every decision, including those
   reviewed in groups. Each decision is recorded per record in
   [`records_screened.csv`](../data/screening/records_screened.csv), next to the tool's
   suggestion and the author who validated it (`validated_by`).
2. **Full text.** I4 first (conditions A and B), then I2/I5, then the quality grid.
   Boundary cases were adjudicated with the second author. Per-report outcomes:
   [`full_text_assessment.csv`](../data/screening/full_text_assessment.csv).
3. **Citation searching.** Backward citation searching in the reference lists of selected
   surveys (`SV` records) and of reports assessed in full text (`BT` records), plus one
   expert recommendation (FLORA). Same criteria and quality grid. Forward citation
   searching was not done.

## 6. Complementary search R4 (amendment, July 2026)

**Why.** Full-text assessment showed that systems whose symbolic operation really
participates in matching often describe themselves by their reasoning mechanism
(reasoner, description logic, fuzzy logic, formal concept analysis, ...) rather than by a
"neuro-symbolic" or "hybrid" label. The primary queries did not cover this vocabulary, which
produced eligible false negatives (two such studies had been found outside the corpus).

**How.**
- Same databases, period, document types, criteria and quality procedure; one query R4
  combining a reasoning-mechanism block with neural and task blocks.
- Duplicates removed within the batch, then against every record already handled (primary
  records, citation searching, expert recommendation): exact DOI, title similarity of at
  least 95 % after canonicalisation (e.g. KG expanded to knowledge graph), preprint/published
  twins (year +/- 1), and one manual match.
- Screening support unchanged. Because relevance scores are rescaled within the corpus,
  R4 records were scored together with the primary records and only R4 records were screened.
- **Recapture test** (blocking): the batch had to contain the two eligible studies that
  revealed the gap (ReasonAlign and LLM4EA). It did.
- Processed in one exhaustive pass, then closed. Earlier exclusions were not reopened.

**Reporting.** R4 is a second, dated identification stream within the single PRISMA
flow, not a review update and not "other methods".

## 7. Data extraction and coding (Section 3.3)

Three linked units: **studies** (metadata, task, quality, provenance), **mechanisms**
(neural and symbolic components and their interaction) and **configurations** (dataset,
setting, metrics, baselines, results). Every value was coded or validated by the first
author against the full text. Definitions and rules:
[coding_guide.md](coding_guide.md).

Because RQ2 rests on negative findings, all 27 studies were audited for an expert feedback
loop, an explanation user study and a human-effort measure.

## 8. Synthesis

Structured narrative synthesis; no meta-analysis (tasks, datasets and metrics are too
heterogeneous). The study is the unit of analysis. Multi-valued codes keep all supported
roles, and one dominant value is used for counts. Mixed-stage studies keep their dominant
stage; the one stage code flagged as sensitive (DeepFCA) is reclassified in a sensitivity analysis.

## 9. Amendments and deviations

| What changed | When | Effect |
|---|---|---|
| arXiv added as a source and preprints admitted (I1 exception) | before searching | 189 primary and 163 R4 records; preprint status recorded; peer-reviewed versions identified later are used for citation, the assessed version for eligibility and coding |
| I3, I4 and E1 reworded; I4 baseline clause moved to extraction | before screening | I3 now targets explainability/HITL; inter-KG entity alignment explicitly eligible |
| Quality grid revised (Q4 explainability/HITL, Q5 external baseline, Q6 unscored) | before quality assessment | - |
| **I4 revised** from "symbolic component active at inference" (I4-strict) to "symbolic component participates in the matcher" (conditions A and B); stage becomes an analysis variable | during full-text assessment | studies whose symbolic operation acts during training became eligible; previous I4-strict exclusions were re-audited for false negatives, targeting high-risk candidates (neural + symbolic + matching task) rather than re-reading all of them; five studies were reinstated |
| Repair and revision tasks counted as matching under I2 | during full-text assessment | one study included (PLM ontology revision) |
| Reports whose full text is only in a language the team cannot read excluded (coded E6) | during full-text assessment | four reports, all in Chinese (three primary, one R4) |
| **Complementary search R4** | July 2026 | 954 records, 820 screened, 8 studies added (section 6) |
| Coding grid reduced: infusion level (D1) and linking strategy (D4) dropped | during extraction | could not be coded reliably |
| Web of Science not searched | - | no institutional access to advanced search; partly covered by Scopus |
