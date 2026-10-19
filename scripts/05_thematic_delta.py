"""Thematic composition of the identified corpus versus the included studies (fig:thematic-delta).

The twelve clusters of the VOSviewer map of the identified corpus (fig:vos-network) are
grouped into five macro-themes. A record carries a theme when one of its author
keywords, or a keyword of that theme found in its title or abstract, belongs to
one of the theme's clusters (after thesaurus normalisation). Themes are multi-label.

Needs titles and abstracts, so it runs on data/interim/ (from 02_deduplicate.py)
and data/raw/citation_searching_abstracts.csv.

  figures/thematic_composition.pdf
  results/thematic_delta.csv
"""

import json
import re

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import EXTRACTION, FIGURES, INTERIM, RAW, RESULTS, SCREENING, VOSVIEWER

matplotlib.use("Agg")

MACRO_THEMES = {   # VOSviewer cluster numbers of the identified-corpus map
    "Semantic integration\n& ontology matching": [1, 8],
    "Deep learning\n& neural architectures": [2, 3],
    "XAI & symbolic\nreasoning": [4, 6, 11, 12],
    "NLP & language\nmodels": [5, 9, 10],
    "Knowledge graphs\n& neuro-symbolic": [7],
}

th = pd.read_csv(VOSVIEWER / "thesaurus_identified.txt", sep="\t")
thesaurus = dict(zip(th["label"].str.lower().str.strip(), th["replace by"].str.lower().str.strip()))
items = json.load(open(VOSVIEWER / "map_identified.json", encoding="utf-8-sig"))["network"]["items"]
kw_theme = {}
for theme, clusters in MACRO_THEMES.items():
    for it in items:
        if it["cluster"] in clusters:
            kw_theme[str(it["label"]).lower().strip()] = theme
by_length = sorted(kw_theme, key=len, reverse=True)


def themes(title, abstract, keywords):
    found = set()
    for kw in str(keywords).replace(";", ",").split(","):
        kw = thesaurus.get(kw.lower().strip(), kw.lower().strip())
        if kw in kw_theme:
            found.add(kw_theme[kw])
    text = f"{title} {abstract}".lower()
    for kw in by_length:
        if re.search(r"\b" + re.escape(kw) + r"\b", text):
            found.add(kw_theme[kw])
    for label, canon in thesaurus.items():
        if canon in kw_theme and re.search(r"\b" + re.escape(label) + r"\b", text):
            found.add(kw_theme[canon])
    return found


def shares(df):
    counts = {t: 0 for t in MACRO_THEMES}
    for _, r in df.iterrows():
        for t in themes(r["title"], r["abstract"], r["keywords"]):
            counts[t] += 1
    return counts


if __name__ == "__main__":
    read = lambda p: pd.read_csv(p, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    corpus = pd.concat([read(INTERIM / "primary_records.csv"), read(INTERIM / "complementary_records.csv")],
                       ignore_index=True)
    text_by_title = {t.lower().strip(): (a, k) for t, a, k in
                     zip(corpus["title"], corpus["abstract"], corpus["keywords"])}
    cit = read(RAW / "citation_searching_abstracts.csv").set_index("record_id")
    records = read(SCREENING / "records_screened.csv")
    title_of = dict(zip(records["fulltext_id"], records["title"]))

    rows = []
    for sid in read(EXTRACTION / "studies.csv")["study_id"]:
        if sid in cit.index:
            r = cit.loc[sid]
            rows.append(dict(title=r["title"], abstract=r["abstract"], keywords=r["keywords"]))
        else:
            title = title_of[sid]
            abstract, keywords = text_by_title[title.lower().strip()]
            rows.append(dict(title=title, abstract=abstract, keywords=keywords))
    included = pd.DataFrame(rows)

    c, i = shares(corpus), shares(included)
    n_c, n_i = len(corpus), len(included)
    table = pd.DataFrame([{
        "macro_theme": t.replace("\n", " "),
        "n_identified": c[t], "pct_identified": round(c[t] / n_c * 100, 1),
        "n_included": i[t], "pct_included": round(i[t] / n_i * 100, 1),
        "difference_pp": round(round(i[t] / n_i * 100, 1) - round(c[t] / n_c * 100, 1), 1),
    } for t in MACRO_THEMES])
    table.to_csv(RESULTS / "thematic_delta.csv", index=False)
    print(table.to_string(index=False))

    x, w = np.arange(len(MACRO_THEMES)), 0.35
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.bar(x - w / 2, table["pct_identified"], w, label=f"Identified corpus (N={n_c})", color="#a3c4d9",
           edgecolor="white", zorder=3)
    ax.bar(x + w / 2, table["pct_included"], w, label=f"Included studies (N={n_i})", color="#2c5f8a",
           edgecolor="white", zorder=3)
    for k, (a, b) in enumerate(zip(table["pct_identified"], table["pct_included"])):
        d = b - a
        ax.annotate(f"{d:+.1f} pp", xy=(x[k], max(a, b) + 1.5), ha="center", va="bottom", fontsize=9,
                    fontweight="bold", color="#6b9e6b" if d > 0 else "#c44e52")
    ax.set_xticks(x)
    ax.set_xticklabels(list(MACRO_THEMES), fontsize=9)
    ax.set_ylabel("Proportion of articles (%)")
    ax.set_title("Thematic delta — identified corpus vs. included studies", fontweight="bold", fontsize=13)
    ax.set_ylim(0, max(table["pct_identified"].max(), table["pct_included"].max()) + 8)
    ax.legend(loc="upper right", frameon=True, edgecolor="#cccccc")
    ax.grid(axis="y", alpha=0.3, zorder=0)
    ax.spines[["top", "right"]].set_visible(False)
    for ext in ("pdf", "png"):
        fig.savefig(FIGURES / f"thematic_composition.{ext}", dpi=300, bbox_inches="tight")
