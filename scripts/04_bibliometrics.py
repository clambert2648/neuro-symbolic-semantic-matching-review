"""Descriptive bibliometrics of the search results and of the included studies.

  figures/included_studies_by_year.pdf year and provenance of the 27 studies
  results/cross_database_overlap.csv           cross-database overlap (supplementary material)
  vosviewer/identified_records.ris             input for fig:vos-network and fig:vos-overlay (2,708 records)

The keyword maps themselves are made in VOSviewer; see vosviewer/README.md.
Runs on the versioned data only.
"""

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import DATABASES, EXTRACTION, FIGURES, RESULTS, SCREENING, VOSVIEWER

matplotlib.use("Agg")
plt.rcParams.update({"font.family": "sans-serif", "font.size": 11, "axes.titlesize": 13,
                     "axes.titleweight": "bold", "savefig.bbox": "tight", "savefig.pad_inches": 0.15})


def figure_10(studies):
    route = studies["route"].map({
        "database (primary)": "Database search", "expert recommendation": "Database search",
        "citation searching": "Snowballing", "database (complementary R4)": "Complementary (R4)",
    })
    years = list(range(2020, 2026))
    colors = {"Database search": "#2c5f8a", "Snowballing": "#d4a03c", "Complementary (R4)": "#6b9e6b"}
    year = studies["year_assessed"].astype(int)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    bottom = np.zeros(len(years))
    for cat, color in colors.items():
        vals = np.array([((route == cat) & (year == y)).sum() for y in years])
        ax.bar(years, vals, bottom=bottom, color=color, label=cat, zorder=3)
        bottom += vals
    for x, total in zip(years, bottom):
        ax.text(x, total + 0.15, str(int(total)), ha="center", va="bottom", fontweight="bold", fontsize=10)
    ax.set_xlabel("Publication year")
    ax.set_ylabel("Number of studies")
    ax.set_title(f"Temporal distribution of included studies (N={len(studies)})")
    ax.set_xticks(years)
    ax.set_ylim(top=bottom.max() + 2)
    ax.legend(frameon=True, edgecolor="#cccccc")
    ax.grid(axis="y", alpha=0.3, zorder=0)
    ax.spines[["top", "right"]].set_visible(False)
    for ext in ("pdf", "png"):
        fig.savefig(FIGURES / f"included_studies_by_year.{ext}", dpi=300)
    plt.close(fig)
    print("Included studies per year", {y: int(n) for y, n in zip(years, bottom)})
    print("           provenance", route.value_counts().to_dict())


def overlap(records):
    m = pd.DataFrame(0, index=DATABASES, columns=DATABASES)
    for value in records["databases"]:
        dbs = [d for d in value.split("+") if d in DATABASES]
        for a in dbs:
            for b in dbs:
                m.loc[a, b] += 1
    m.to_csv(RESULTS / "cross_database_overlap.csv")
    print("\nCross-database overlap (diagonal = records retrieved by each database)\n", m)


def ris(records, path):
    lines = []
    for _, r in records.iterrows():
        kind = "CPAPER" if any(k in r["doc_type"].lower() for k in ("conference", "proceeding", "workshop")) else "JOUR"
        lines.append(f"TY  - {kind}")
        for tag, col in [("TI", "title"), ("PY", "year"), ("JO", "venue"), ("DO", "doi")]:
            if r[col].strip():
                lines.append(f"{tag}  - {r[col].strip()}")
        # Split on ";" as in the original analysis. ACM exports separate keywords with
        # commas, so an ACM record contributes one combined KW line.
        lines += [f"KW  - {k.strip()}" for k in r["author_keywords"].split(";") if k.strip()]
        lines += [f"AU  - {a.strip()}" for a in r["authors"].split(";") if a.strip()]
        lines += ["ER  - ", ""]
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n{path.name}: {len(records)} records, "
          f"{(records['author_keywords'].str.strip() != '').sum()} with author keywords")


if __name__ == "__main__":
    FIGURES.mkdir(exist_ok=True)
    RESULTS.mkdir(exist_ok=True)
    studies = pd.read_csv(EXTRACTION / "studies.csv", dtype=str, keep_default_na=False)
    records = pd.read_csv(SCREENING / "records_screened.csv", dtype=str, keep_default_na=False)
    figure_10(studies)
    overlap(records)
    ris(records, VOSVIEWER / "identified_records.ris")
