"""Merge and deduplicate the database exports (Section 3.1; identification part of fig:prisma).

Primary wave (R1-R3, 27 Feb 2026)
    1. load the 16 exports (4 databases x 4 queries; ACM book chapters dropped)
    2. deduplicate within each database (exact DOI, then title >= 95 % with same year)
    3. deduplicate between databases (same two passes)
    4. drop records dated outside 2020-2025 (E6, before screening)

Complementary wave (R4, 14 Jul 2026)
    1. load the 4 exports and deduplicate within the batch
    2. remove records already handled in the primary wave or by citation searching
       (exact DOI, canonical title >= 95 % with same year, one manual match,
       then preprint/published twins of those matches with year +/- 1)

Needs data/raw/ (see data/raw/README.md). Writes data/interim/*.csv and prints
the identification counts of the PRISMA flow diagram (fig:prisma).
"""

import pandas as pd

from common import (DATABASES, FUZZY_THRESHOLD, INTERIM, PRIMARY_QUERIES, SCREENING,
                    canonical_title, deduplicate, load_export, title_score)

# Same work, different venue and DOI: found by manual check, invisible to DOI
# and title matching. Key: DOI of the R4 record; value: record already screened.
MANUAL_DUPLICATES = {"10.1109/icmla52953.2021.00155": "093 (OntoConnect, ICMLA 2021 version)"}


def primary_wave():
    counts, per_db = {}, []
    for db in ["scopus", "ieee", "acm", "arxiv"]:
        raw = pd.concat([load_export(db, q) for q in PRIMARY_QUERIES], ignore_index=True)
        dedup, _, _ = deduplicate(raw, "query", PRIMARY_QUERIES, fuzzy_on="no_doi")
        counts[f"{db} records"] = len(raw)
        counts[f"{db} after within-database deduplication"] = len(dedup)
        per_db.append(dedup)
    combined = pd.concat(per_db, ignore_index=True)
    merged, _, _ = deduplicate(combined, "database", DATABASES, fuzzy_on="no_doi")
    year = pd.to_numeric(merged["year"], errors="coerce")
    in_window = year.between(2020, 2025)
    screened = merged[in_window].reset_index(drop=True)

    counts["records identified"] = sum(v for k, v in counts.items() if k.endswith(" records"))
    counts["within-database duplicates"] = counts["records identified"] - len(combined)
    counts["between-database duplicates"] = len(combined) - len(merged)
    counts["removed before screening (E6)"] = int((~in_window).sum())
    counts["records screened"] = len(screened)
    return screened, counts


def already_screened_reference():
    """Titles, years and DOIs of every record handled before the R4 search."""
    records = pd.read_csv(SCREENING / "records_screened.csv", dtype=str, keep_default_na=False)
    citations = pd.read_csv(SCREENING / "citation_searching.csv", dtype=str, keep_default_na=False)
    ref = pd.concat([records[records["wave"] == "primary"], citations], ignore_index=True)
    return pd.DataFrame({
        "canon": ref["title"].map(canonical_title),
        "year": ref["year"].str.strip(),
        "doi": ref["doi"].str.lower().str.strip(),
        "id": ref["record_id"],
    })


def complementary_wave():
    counts = {}
    exports = {db: load_export(db, "R4") for db in ["scopus", "ieee", "acm", "arxiv"]}
    for db, frame in exports.items():
        counts[f"R4 {db} records"] = len(frame)
    raw = pd.concat(exports.values(), ignore_index=True)
    batch, _, _ = deduplicate(raw, "database", DATABASES, fuzzy_on="all")
    counts["R4 records identified"] = len(raw)
    counts["R4 duplicates within the batch"] = len(raw) - len(batch)

    ref = already_screened_reference()
    ref = ref[ref["canon"] != ""]
    ref_dois = dict(zip(ref["doi"], ref["id"]))
    ref_dois.pop("", None)

    matched = []
    for _, row in batch.iterrows():
        doi = str(row["doi"]).lower().strip()
        if doi in MANUAL_DUPLICATES:
            matched.append(("manual", MANUAL_DUPLICATES[doi]))
            continue
        if doi and doi in ref_dois:
            matched.append(("doi", ref_dois[doi]))
            continue
        canon, year = canonical_title(row["title"]), str(row["year"]).strip()
        hit = ""
        if canon:
            for c, y, rid in zip(ref["canon"], ref["year"], ref["id"]):
                if title_score(canon, c) >= FUZZY_THRESHOLD and (year == y or "" in (year, y)):
                    hit = rid
                    break
        matched.append(("title", hit) if hit else ("", ""))
    batch["match"] = [m for m, _ in matched]
    batch["matched_id"] = [i for _, i in matched]

    # Preprint/published twins of a record matched above (year +/- 1).
    dup = batch[batch["match"] != ""]
    dup_keys = list(zip(dup["title"].map(canonical_title), pd.to_numeric(dup["year"], errors="coerce")))
    for i in batch.index[batch["match"] == ""]:
        canon, year = canonical_title(batch.at[i, "title"]), pd.to_numeric(batch.at[i, "year"], errors="coerce")
        for c, y in dup_keys:
            if canon and title_score(canon, c) >= FUZZY_THRESHOLD and abs(year - y) <= 1:
                batch.at[i, "match"] = "twin"
                break

    delta = batch[batch["match"] == ""].drop(columns=["match", "matched_id"]).reset_index(drop=True)
    counts["R4 records already screened"] = int((batch["match"] != "").sum())
    counts["R4 records screened"] = len(delta)
    batch[batch["match"] != ""].to_csv(INTERIM / "complementary_already_screened.csv",
                                       index=False, encoding="utf-8-sig")
    return delta, counts


if __name__ == "__main__":
    INTERIM.mkdir(parents=True, exist_ok=True)
    primary, c1 = primary_wave()
    primary.to_csv(INTERIM / "primary_records.csv", index=False, encoding="utf-8-sig")
    complementary, c2 = complementary_wave()
    complementary["query"] = "R4"
    complementary.to_csv(INTERIM / "complementary_records.csv", index=False, encoding="utf-8-sig")

    counts = {**c1, **c2, "total records screened": len(primary) + len(complementary)}
    pd.Series(counts, name="n").rename_axis("step").to_csv(SCREENING / "identification_counts.csv")
    for name, n in counts.items():
        print(f"{name:<48}{n:>6}")
