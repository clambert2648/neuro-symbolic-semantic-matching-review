# Search strings

Full search strategies for the four databases, as run. This file is the
supplementary material on search strings cited in *Search strategy* (Section 3.1) of the article.

- Primary search (R1, R2A, R2B, R3): run on **27 February 2026**.
- Complementary reasoning-mechanism search (R4): run on **14 July 2026**.
- Publication window: 2020-2025. Document types: journal articles and conference papers
  (arXiv preprints admitted under the protocol exception, see [protocol.md](protocol.md)).
- The raw exports are listed in [`data/raw/README.md`](../data/raw/README.md).

## Records retrieved

| Query | Focus | Scopus | IEEE Xplore | ACM DL | arXiv | Total |
|---|---|---:|---:|---:|---:|---:|
| R1 | Semantic matching + NLP/KG | 296 | 158 | 81 | 143 | 678 |
| R2A | Explicit neuro-symbolic methods | 312 | 82 | 28 | 25 | 447 |
| R2B | Implicit neural-symbolic hybrid | 510 | 237 | 123 | 20 | 890 |
| R3 | M&E and multilingual context | 101 | 117 | 36 | 1 | 255 |
| **Primary total** | | **1,219** | **594** | **268** | **189** | **2,270** |
| R4 | Named reasoning mechanisms | 245 | 335 | 211 | 163 | 954 |

Counts are after the interface filters described below. Two filters are applied
after the query and change the count, so the strings alone do not reproduce it:

- **ACM**: the exports for R1-R3 contained 16 book chapters (`@inbook`: 1, 1, 7 and 7),
  dropped under E5. The interface showed 82, 29, 130 and 43 records before this filter.
  `scripts/02_deduplicate.py` drops them when loading.
- **IEEE R4**: 343 records with the year filter only; the Content Type filter
  (Conferences 266 + Journals 69) excludes 5 magazine items and 3 books, giving 335.

## Scopus

Field `TITLE-ABS-KEY`, wildcards supported.

**R1 - semantic harmonisation + NLP/KG** (296)
```
TITLE-ABS-KEY((
  ("data harmonization" OR "data harmonisation" OR "variable harmonization" OR
   "variable harmonisation" OR "semantic harmonization" OR "semantic harmonisation" OR
   "semantic integration" OR "data alignment" OR "schema alignment" OR
   "schema matching" OR "ontology alignment" OR "ontology matching" OR "variable mapping")
  AND
  (indicator* OR variable* OR item* OR questionnaire OR "survey instrument*" OR
   "survey question*" OR metadata OR "data dictionary" OR codebook OR
   "common data element*" OR CDE OR "data schema" OR attribute* OR column* OR
   header* OR field* OR "data element*")
  AND
  ("natural language processing" OR NLP OR "text mining" OR embedding* OR
   "text similarity" OR "semantic similarity" OR "language model*" OR
   "large language model*" OR transformer* OR "knowledge graph*" OR ontology)
)) AND PUBYEAR > 2019 AND PUBYEAR < 2026 AND (DOCTYPE(ar) OR DOCTYPE(cp))
```

**R2A - explicit neuro-symbolic** (312)
```
TITLE-ABS-KEY(
  ("neuro-symbolic" OR neurosymbolic OR "neural-symbolic" OR "neural symbolic" OR
   "neuro symbolic" OR "hybrid neural symbolic")
  AND ("knowledge graph*" OR ontology OR ontologies OR "semantic network*" OR
   "knowledge base*")
  AND (reasoning OR inference OR matching OR alignment OR "entity resolution" OR
   "schema matching" OR "ontology alignment" OR "entity linking" OR "link prediction" OR
   explainab* OR interpretab*)
) AND PUBYEAR > 2019 AND PUBYEAR < 2026 AND (DOCTYPE(ar) OR DOCTYPE(cp))
```

**R2B - implicit neural + symbolic hybrid** (510). The integration terms are restricted
to the title; pilot runs went from 3,837 to 511 records without losing the known relevant papers.
```
TITLE((hybrid OR combin* OR integrat* OR fusion OR joint OR "neural symbolic" OR
  "symbolic neural" OR "knowledge graph enhanced" OR "ontology-guided" OR "logic-guided"))
AND TITLE-ABS-KEY(
  (("neural network*" OR "deep learning" OR embedding* OR transformer* OR
    "language model*" OR "large language model*" OR BERT OR GPT)
   AND (ontology OR ontologies OR "knowledge graph*" OR "knowledge base*"))
  AND (matching OR alignment OR "entity resolution" OR "entity linking" OR
   "schema matching" OR "schema alignment" OR "ontology alignment" OR "ontology matching" OR
   "column matching" OR "attribute matching" OR explainab* OR interpretab*)
) AND PUBYEAR > 2019 AND PUBYEAR < 2026 AND (DOCTYPE(ar) OR DOCTYPE(cp))
```

**R3 - M&E and multilingual context** (101)
```
TITLE-ABS-KEY((
  ("data matching" OR "variable mapping" OR "indicator alignment" OR
   "data harmonization" OR "data harmonisation" OR "semantic matching" OR
   "semantic integration" OR "variable harmonization" OR "variable harmonisation")
  AND (questionnaire* OR "survey instrument*" OR "survey question*" OR indicator* OR
   item* OR "monitoring and evaluation" OR "M&E" OR "results measurement" OR
   "results framework" OR logframe OR "logical framework" OR
   "performance measurement framework" OR "development project*" OR
   "international development" OR "program evaluation" OR "cross-national" OR
   "cross-country" OR "comparative survey*" OR multilingual OR "multi-lingual" OR
   cross-lingual OR crosslingual OR bilingual OR "machine translation")
  AND ("machine learning" OR "deep learning" OR AI OR "artificial intelligence" OR
   NLP OR "natural language processing" OR embedding* OR transformer* OR
   "language model*" OR "large language model*" OR LLM OR "text mining" OR
   "knowledge graph*" OR ontology)
)) AND PUBYEAR > 2019 AND PUBYEAR < 2026 AND (DOCTYPE(ar) OR DOCTYPE(cp))
```

**R4 - named reasoning mechanisms** (245)
```
TITLE-ABS-KEY(
  ("description logic" OR "logical reasoning" OR "symbolic reasoning" OR
   "fuzzy logic" OR "probabilistic reasoning" OR "logic-based" OR
   "non-axiomatic logic" OR "formal concept analysis" OR "logical constraint*" OR
   "logical rule*" OR reasoner)
  AND ("neural network*" OR "deep learning" OR embedding* OR transformer* OR
   "language model*" OR BERT OR "graph neural network*" OR GNN)
  AND (matching OR alignment OR "entity resolution" OR "entity alignment" OR
   "schema matching" OR "ontology alignment" OR "ontology matching")
) AND PUBYEAR > 2019 AND PUBYEAR < 2026 AND (DOCTYPE(ar) OR DOCTYPE(cp))
```

## IEEE Xplore

Interface filters: Year 2020-2025; Content Type Journals + Conference Publications.
IEEE does not expand plurals and does not accept wildcards inside quotes, so both forms
are written out (`"survey instrument"` OR `"survey instruments"`).

**R1** (158)
```
("All Metadata":"data harmonization" OR "All Metadata":"data harmonisation" OR
"All Metadata":"variable harmonization" OR "All Metadata":"variable harmonisation" OR
"All Metadata":"semantic harmonization" OR "All Metadata":"semantic harmonisation" OR
"All Metadata":"semantic integration" OR "All Metadata":"data alignment" OR
"All Metadata":"schema alignment" OR "All Metadata":"schema matching" OR
"All Metadata":"ontology alignment" OR "All Metadata":"ontology matching" OR
"All Metadata":"variable mapping")
AND
("All Metadata":indicator* OR "All Metadata":variable* OR "All Metadata":item* OR
"All Metadata":questionnaire* OR
"All Metadata":"survey instrument" OR "All Metadata":"survey instruments" OR
"All Metadata":"survey question" OR "All Metadata":"survey questions" OR
"All Metadata":metadata OR "All Metadata":"data dictionary" OR "All Metadata":codebook OR
"All Metadata":"common data element" OR "All Metadata":"common data elements" OR
"All Metadata":CDE OR "All Metadata":"data schema" OR
"All Metadata":attribute* OR "All Metadata":column* OR "All Metadata":header* OR
"All Metadata":field* OR "All Metadata":"data element" OR "All Metadata":"data elements")
AND
("All Metadata":"natural language processing" OR "All Metadata":NLP OR
"All Metadata":"text mining" OR "All Metadata":embedding* OR
"All Metadata":"text similarity" OR "All Metadata":"semantic similarity" OR
"All Metadata":"language model" OR "All Metadata":"language models" OR
"All Metadata":"large language model" OR "All Metadata":"large language models" OR
"All Metadata":transformer* OR
"All Metadata":"knowledge graph" OR "All Metadata":"knowledge graphs" OR
"All Metadata":ontology)
```

**R2A** (82)
```
("All Metadata":"neuro-symbolic" OR "All Metadata":neurosymbolic OR
"All Metadata":"neural-symbolic" OR "All Metadata":"neural symbolic" OR
"All Metadata":"neuro symbolic" OR "All Metadata":"hybrid neural symbolic")
AND
("All Metadata":"knowledge graph" OR "All Metadata":"knowledge graphs" OR
"All Metadata":ontology OR "All Metadata":ontologies OR
"All Metadata":"semantic network" OR "All Metadata":"semantic networks" OR
"All Metadata":"knowledge base" OR "All Metadata":"knowledge bases")
AND
("All Metadata":reasoning OR "All Metadata":inference OR "All Metadata":matching OR
"All Metadata":alignment OR "All Metadata":"entity resolution" OR
"All Metadata":"schema matching" OR "All Metadata":"ontology alignment" OR
"All Metadata":"entity linking" OR "All Metadata":"link prediction" OR
"All Metadata":explainab* OR "All Metadata":interpretab*)
```

**R2B** (237)
```
("Document Title":hybrid OR "Document Title":combin* OR "Document Title":integrat* OR
"Document Title":fusion OR "Document Title":joint OR
"Document Title":"neural symbolic" OR "Document Title":"symbolic neural" OR
"Document Title":"knowledge graph enhanced" OR "Document Title":"ontology-guided" OR
"Document Title":"logic-guided")
AND
("All Metadata":"neural network" OR "All Metadata":"neural networks" OR
"All Metadata":"deep learning" OR "All Metadata":embedding* OR
"All Metadata":transformer* OR
"All Metadata":"language model" OR "All Metadata":"language models" OR
"All Metadata":"large language model" OR "All Metadata":"large language models" OR
"All Metadata":BERT OR "All Metadata":GPT)
AND
("All Metadata":ontology OR "All Metadata":ontologies OR
"All Metadata":"knowledge graph" OR "All Metadata":"knowledge graphs" OR
"All Metadata":"knowledge base" OR "All Metadata":"knowledge bases")
AND
("All Metadata":matching OR "All Metadata":alignment OR
"All Metadata":"entity resolution" OR "All Metadata":"entity linking" OR
"All Metadata":"schema matching" OR "All Metadata":"schema alignment" OR
"All Metadata":"ontology alignment" OR "All Metadata":"ontology matching" OR
"All Metadata":"column matching" OR "All Metadata":"attribute matching" OR
"All Metadata":explainab* OR "All Metadata":interpretab*)
```

**R3** (117)
```
("All Metadata":"data matching" OR "All Metadata":"variable mapping" OR
"All Metadata":"indicator alignment" OR "All Metadata":"data harmonization" OR
"All Metadata":"data harmonisation" OR "All Metadata":"semantic matching" OR
"All Metadata":"semantic integration" OR "All Metadata":"variable harmonization" OR
"All Metadata":"variable harmonisation")
AND
("All Metadata":questionnaire* OR
"All Metadata":"survey instrument" OR "All Metadata":"survey instruments" OR
"All Metadata":"survey question" OR "All Metadata":"survey questions" OR
"All Metadata":indicator* OR
"All Metadata":"monitoring and evaluation" OR "All Metadata":"results measurement" OR
"All Metadata":"results framework" OR "All Metadata":logframe OR
"All Metadata":"logical framework" OR "All Metadata":"international development" OR
"All Metadata":"program evaluation" OR "All Metadata":"cross-national" OR
"All Metadata":"cross-country" OR
"All Metadata":"comparative survey" OR "All Metadata":"comparative surveys" OR
"All Metadata":multilingual OR "All Metadata":"multi-lingual" OR
"All Metadata":cross-lingual OR "All Metadata":crosslingual OR
"All Metadata":bilingual OR "All Metadata":"machine translation" OR
"All Metadata":"development project" OR "All Metadata":"development projects")
AND
("All Metadata":"machine learning" OR "All Metadata":"deep learning" OR
"All Metadata":"artificial intelligence" OR "All Metadata":NLP OR
"All Metadata":"natural language processing" OR "All Metadata":embedding* OR
"All Metadata":transformer* OR
"All Metadata":"language model" OR "All Metadata":"language models" OR
"All Metadata":"large language model" OR "All Metadata":"large language models" OR
"All Metadata":"text mining" OR
"All Metadata":"knowledge graph" OR "All Metadata":"knowledge graphs" OR
"All Metadata":ontology)
```

**R4** (343 with the year filter, 335 after the Content Type filter). No field prefix:
IEEE searches metadata by default, which is the intended behaviour.
```
((("description logic" OR "logical reasoning" OR "symbolic reasoning" OR
"fuzzy logic" OR "probabilistic reasoning" OR "logic-based" OR
"non-axiomatic logic" OR "formal concept analysis" OR
"logical constraint" OR "logical constraints" OR
"logical rule" OR "logical rules" OR reasoner)
AND
("neural network" OR "neural networks" OR "deep learning" OR
embedding OR embeddings OR transformer OR transformers OR
"language model" OR "language models" OR BERT OR
"graph neural network" OR "graph neural networks" OR GNN)
AND
(matching OR alignment OR "entity resolution" OR "entity alignment" OR
"schema matching" OR "ontology alignment" OR "ontology matching")))
```

## ACM Digital Library

Collection: ACM Full-Text Collection (not the Guide to Computing Literature).
Interface filters: E-Publication Date 01/01/2020-31/12/2025; Content Type Research Article.
Field: Abstract, via *Search Within* (Title + Abstract returned no results), except where noted.
ACM does not handle wildcards like Scopus; it applies a light stemming.

**R1** (82 shown, 81 kept)
```
Line 1 - Abstract, AND:
"data harmonization" OR "data harmonisation" OR "variable harmonization" OR "variable harmonisation" OR "semantic harmonization" OR "semantic harmonisation" OR "semantic integration" OR "data alignment" OR "schema alignment" OR "schema matching" OR "ontology alignment" OR "ontology matching" OR "variable mapping"
Line 2 - Abstract, AND:
indicator* OR variable* OR item* OR questionnaire* OR "survey instrument" OR "survey instruments" OR "survey question" OR "survey questions" OR metadata OR "data dictionary" OR codebook OR "common data element" OR "common data elements" OR CDE OR "data schema" OR attribute* OR column* OR header* OR field* OR "data element" OR "data elements"
Line 3 - Abstract:
"natural language processing" OR NLP OR "text mining" OR embedding* OR "text similarity" OR "semantic similarity" OR "language model" OR "language models" OR "large language model" OR "large language models" OR transformer* OR "knowledge graph" OR "knowledge graphs" OR ontology
```

**R2A** (29 shown, 28 kept)
```
Line 1 - Abstract, AND:
"neuro-symbolic" OR neurosymbolic OR "neural-symbolic" OR "neural symbolic" OR "neuro symbolic" OR "hybrid neural symbolic"
Line 2 - Abstract, AND:
"knowledge graph" OR "knowledge graphs" OR ontology OR ontologies OR "semantic network" OR "semantic networks" OR "knowledge base" OR "knowledge bases"
Line 3 - Abstract:
reasoning OR inference OR matching OR alignment OR "entity resolution" OR "schema matching" OR "ontology alignment" OR "entity linking" OR "link prediction" OR explainab* OR interpretab*
```

**R2B** (130 shown, 123 kept)
```
Line 1 - Title, AND:
hybrid OR combin* OR integrat* OR fusion OR joint OR "neural symbolic" OR "symbolic neural" OR "knowledge graph enhanced" OR "ontology-guided" OR "logic-guided"
Line 2 - Abstract, AND:
"neural network" OR "neural networks" OR "deep learning" OR embedding* OR transformer* OR "language model" OR "language models" OR "large language model" OR "large language models" OR BERT OR GPT
Line 3 - Abstract, AND:
ontology OR ontologies OR "knowledge graph" OR "knowledge graphs" OR "knowledge base" OR "knowledge bases"
Line 4 - Abstract:
matching OR alignment OR "entity resolution" OR "entity linking" OR "schema matching" OR "schema alignment" OR "ontology alignment" OR "ontology matching" OR "column matching" OR "attribute matching" OR explainab* OR interpretab*
```

**R3** (43 shown, 36 kept)
```
Line 1 - Abstract, AND:
"data matching" OR "variable mapping" OR "indicator alignment" OR "data harmonization" OR "data harmonisation" OR "semantic matching" OR "semantic integration" OR "variable harmonization" OR "variable harmonisation"
Line 2 - Abstract, AND:
questionnaire* OR "survey instrument" OR "survey instruments" OR "survey question" OR "survey questions" OR indicator* OR "monitoring and evaluation" OR "results measurement" OR "results framework" OR logframe OR "logical framework" OR "international development" OR "program evaluation" OR "cross-national" OR "cross-country" OR "comparative survey" OR "comparative surveys" OR multilingual OR "multi-lingual" OR cross-lingual OR crosslingual OR bilingual OR "machine translation" OR "development project" OR "development projects"
Line 3 - Abstract:
"machine learning" OR "deep learning" OR AI OR "artificial intelligence" OR NLP OR "natural language processing" OR embedding* OR transformer* OR "language model" OR "language models" OR "large language model" OR "large language models" OR LLM OR "text mining" OR "knowledge graph" OR "knowledge graphs" OR ontology
```

**R4** (211)
```
Abstract:("description logic" OR "logical reasoning" OR "symbolic reasoning" OR
"fuzzy logic" OR "probabilistic reasoning" OR "logic-based" OR
"non-axiomatic logic" OR "formal concept analysis" OR
"logical constraint" OR "logical rule" OR reasoner)
AND
Abstract:("neural network" OR "deep learning" OR embedding OR transformer OR
"language model" OR BERT OR "graph neural network" OR GNN)
AND
Abstract:(matching OR alignment OR "entity resolution" OR "entity alignment" OR
"schema matching" OR "ontology alignment" OR "ontology matching")
```

## arXiv

Retrieved through the Python `arxiv` API with [`scripts/01_fetch_arxiv.py`](../scripts/01_fetch_arxiv.py);
years filtered after retrieval. The API does not handle long Boolean expressions
reliably, so the arXiv queries are **simplified** compared with the other databases
(for example, R1 drops the indicator/variable/metadata block). This lowers precision
on arXiv and is reported as a limitation.

**Primary queries** (`max_results=200`, sorted by relevance): R1 143, R2A 25, R2B 20, R3 1.
```python
QUERIES = {
    'R1':  '(abs:"schema matching" OR abs:"ontology alignment" OR '
           'abs:"data harmonization" OR abs:"semantic integration") AND '
           '(abs:"knowledge graph" OR abs:"ontology" OR abs:embedding OR '
           'abs:transformer OR abs:"language model")',
    'R2A': '(abs:"neuro-symbolic" OR abs:neurosymbolic OR abs:"neural-symbolic") AND '
           '(abs:"knowledge graph" OR abs:ontology) AND '
           '(abs:matching OR abs:alignment OR abs:explainab)',
    'R2B': '(ti:hybrid OR ti:integration OR ti:fusion) AND '
           '(abs:"knowledge graph" OR abs:ontology) AND '
           '(abs:"neural network" OR abs:transformer OR abs:embedding) AND '
           '(abs:matching OR abs:alignment)',
    'R3':  '(abs:"data harmonization" OR abs:"semantic matching" OR '
           'abs:"variable mapping") AND (abs:"monitoring and evaluation" OR '
           'abs:multilingual OR abs:"international development") AND '
           '(abs:"machine learning" OR abs:NLP OR abs:transformer)',
}
```

**R4** (163 unique records). A single query combining the reasoning terms returns no
results on the API, so each term is run as its own sub-query and the results are merged
on the arXiv identifier (version suffix removed). Eight reasoning terms are used instead
of eleven: `logic-based`, `logical constraint` and `logical rule` produced noise without
recall gain because of how the API parses hyphenated and multi-word terms.
```python
REASONING = ['"description logic"', '"logical reasoning"', '"symbolic reasoning"',
             '"fuzzy logic"', '"probabilistic reasoning"', '"non-axiomatic logic"',
             '"formal concept analysis"', 'reasoner']
NEURAL = ('(abs:"neural network" OR abs:"deep learning" OR abs:embedding OR '
          'abs:transformer OR abs:"language model" OR abs:BERT OR '
          'abs:"graph neural network" OR abs:GNN)')
TASK   = ('(abs:matching OR abs:alignment OR abs:"entity resolution" OR '
          'abs:"entity alignment" OR abs:"schema matching" OR '
          'abs:"ontology alignment" OR abs:"ontology matching")')
# one sub-query per term: f'abs:{term} AND {NEURAL} AND {TASK}'
# client: page_size=100, delay_seconds=3, num_retries=3; sorted by submission date; max_results=500
```

## Databases not searched

Web of Science was not searched because institutional access to its advanced search
was unavailable (see *Limitations* in the article). Search strings had been adapted to its
syntax but were never run.
