"""Recompute every number reported in the article from the data files and check it.

Inputs (versioned): data/screening/*.csv, data/extraction/*.csv
Outputs:
  results/article_checks.csv           each reported value, the recomputed value, match yes/no
  results/prisma_flow.csv              PRISMA flow counts recomputed from the screening files
  results/fulltext_exclusions.csv      full-text exclusions by recorded basis
  results/table6_stage_by_function.csv Table 6
  results/tableA1_included_studies.csv Table A.1
  figures/evidence_map.pdf             evidence map (C1 and C2 coding of the 27 studies)
"""

from collections import Counter

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Rectangle

from common import EXTRACTION, FIGURES, RESULTS, SCREENING

matplotlib.use("Agg")


def read(path):
    return pd.read_csv(path, dtype=str, keep_default_na=False)


studies = read(EXTRACTION / "studies.csv")
coding = read(EXTRACTION / "coding.csv")
expl = read(EXTRACTION / "explanation_hitl.csv")
context = read(EXTRACTION / "context.csv")
ablation = read(EXTRACTION / "ablation.csv")
audit = read(EXTRACTION / "rq2_audit.csv")
records = read(SCREENING / "records_screened.csv")
citations = read(SCREENING / "citation_searching.csv")
fulltext = read(SCREENING / "full_text_assessment.csv")
ident = read(SCREENING / "identification_counts.csv").set_index("step")["n"].astype(int)

df = (studies.merge(coding.drop(columns="system"), on="study_id")
      .merge(expl.drop(columns="system"), on="study_id")
      .merge(context.drop(columns=["system", "task_family"]), on="study_id")
      .merge(ablation.drop(columns="system"), on="study_id"))
assert len(df) == 27

checks = []


def check(section, claim, article, computed):
    checks.append(dict(section=section, claim=claim, article=str(article), computed=str(computed),
                       match="yes" if str(article) == str(computed) else "NO"))


# --------------------------------------------------------------------------- PRISMA flow (fig:prisma)
prim, comp = records[records.wave == "primary"], records[records.wave == "complementary"]
ft_db = fulltext[fulltext.route.str.startswith("database")]
ft_other = fulltext[~fulltext.route.str.startswith("database")]
# R4-14 (full text only in Chinese) is counted as "not retrieved" in the article's flow diagram.
not_retrieved_db = (ft_db.outcome == "not retrieved").sum() + (ft_db.report_id == "R4-14").sum()
flow = {
    "Records identified from databases": ident["records identified"] + ident["R4 records identified"],
    "  primary queries R1-R3": ident["records identified"],
    "  complementary query R4": ident["R4 records identified"],
    "Records removed before screening": ident["records identified"] + ident["R4 records identified"]
                                        - ident["total records screened"],
    "  duplicates within databases": ident["within-database duplicates"],
    "  duplicates between databases": ident["between-database duplicates"],
    "  duplicates within the R4 batch": ident["R4 duplicates within the batch"],
    "  R4 records already screened in the primary wave": ident["R4 records already screened"],
    "  excluded before screening (E6)": ident["removed before screening (E6)"],
    "Records screened": len(records),
    "Records excluded": (records.ta_decision != "include").sum(),
    "  primary wave": (prim.ta_decision == "exclude").sum(),
    "  complementary wave": (comp.ta_decision != "include").sum(),
    "  surveys kept for citation searching only": (prim.ta_decision == "survey").sum(),
    "Reports sought for retrieval": (records.ta_decision == "include").sum(),
    "Reports not retrieved": not_retrieved_db,
    "Reports assessed for eligibility": (records.ta_decision == "include").sum() - not_retrieved_db,
    "Reports excluded": ((ft_db.outcome == "excluded") & (ft_db.report_id != "R4-14")).sum(),
    "Studies included via databases": (ft_db.outcome == "included").sum(),
    "Records identified from other methods": len(citations),
    "Other methods: reports sought": (citations.ta_decision == "include").sum(),
    "Other methods: reports assessed": len(ft_other),
    "Other methods: reports excluded": (ft_other.outcome == "excluded").sum(),
    "Other methods: studies included": (ft_other.outcome == "included").sum(),
    "Studies included in review": (fulltext.outcome == "included").sum(),
}
ARTICLE_FLOW = [3224, 2270, 954, 516, 106, 274, 94, 40, 2, 2708, 2452, 1613, 780, 59, 256, 12, 244, 221, 23,
            51, 20, 20, 16, 4, 27]
pd.DataFrame({"step": list(flow), "n": [int(v) for v in flow.values()], "article": ARTICLE_FLOW}).to_csv(
    RESULTS / "prisma_flow.csv", index=False)
for (step, n), fig in zip(flow.items(), ARTICLE_FLOW):
    check("fig:prisma", step.strip(), fig, int(n))

excluded = fulltext[fulltext.outcome == "excluded"].copy()
excluded["stream"] = excluded.route.map(lambda r: "databases" if r.startswith("database") else "other methods")
reasons = excluded.groupby(["stream", "basis"]).size().rename("n").reset_index()
reasons.to_csv(RESULTS / "fulltext_exclusions.csv", index=False)

# --------------------------------------------------------------------------- Section 3.4 / 4.1
check("3.3", "studies whose stage and function were coded", 27, len(df))
fam = Counter(df.task_family)
for name, n in [("Entity and knowledge-graph alignment", 13), ("Ontology matching and revision", 9),
                ("Schema matching and data harmonization", 3), ("Entity resolution and record matching", 2)]:
    check("4.1", f"task family: {name}", n, fam[name])
check("3.4", "studies published in 2021 (assessed version)", 7, (df.year_assessed == "2021").sum())
check("3.4", "studies published in 2025 (assessed version)", 9, (df.year_assessed == "2025").sum())
for v, n in [("conference", 13), ("preprint", 8), ("journal", 6)]:
    check("3.4", f"venue type at extraction: {v}", n, (df.venue_type_assessed == v).sum())
route = df.route.replace({"expert recommendation": "database (primary)"})
check("fig:included-years", "provenance: database search incl. expert recommendation", 16, (route == "database (primary)").sum())
check("fig:included-years", "provenance: citation searching", 3, (route == "citation searching").sum())
check("fig:included-years", "provenance: complementary search", 8, (route == "database (complementary R4)").sum())

# --------------------------------------------------------------------------- RQ1
k = Counter(df.kautz_type)
for t, n in [("II", 5), ("III", 8), ("IV", 8), ("V", 6), ("I", 0), ("VI", 0)]:
    check("4.2.1", f"Kautz Type {t}", n, k[t])
check("4.2.1", "logic-based strategy", 24, (df.strategy == "Logic-based").sum())
check("4.2.1", "structure-based strategy", 3, (df.strategy == "Structure-based").sum())
check("4.2.1", "Kautz types of structure-based studies", "III, IV",
      ", ".join(sorted(set(df[df.strategy == "Structure-based"].kautz_type))))
check("4.2.1", "Kautz types of logic-based studies", "II, III, IV, V",
      ", ".join(sorted(set(df[df.strategy == "Logic-based"].kautz_type))))
check("4.2.2", "N2 (inference) dominant", 14, (df.stage == "N2").sum())
check("4.2.2", "N1 (training or preprocessing) dominant", 13, (df.stage == "N1").sum())
check("4.2.2", "N2 share (%)", 52, round((df.stage == "N2").mean() * 100))
check("4.2.2", "mixed-stage studies", 6, (df.mixed_stage == "yes").sum())
check("4.2.2", "mixed-stage, N2-dominant", 4, ((df.mixed_stage == "yes") & (df.stage == "N2")).sum())
check("4.2.2", "mixed-stage, N1-dominant", 2, ((df.mixed_stage == "yes") & (df.stage == "N1")).sum())
sens = df.stage.where(df.system != "DeepFCA", "N2")
check("4.2.2", "sensitivity (DeepFCA to N2): N1 / N2", "12 / 15",
      f"{(sens == 'N1').sum()} / {(sens == 'N2').sum()}")

FUNCS = ["Candidate generation", "Constraint enforcement", "Repair", "Explanation", "Decision"]
table6 = pd.crosstab(df.stage, df.function).reindex(index=["N1", "N2"], columns=FUNCS, fill_value=0)
table6["Total"] = table6.sum(axis=1)
table6.loc["Total"] = table6.sum()
table6.to_csv(RESULTS / "table6_stage_by_function.csv")
TABLE_6 = {"N1": [5, 8, 0, 0, 0, 13], "N2": [1, 2, 2, 1, 8, 14], "Total": [6, 10, 2, 1, 8, 27]}
for stage, values in TABLE_6.items():
    check("Table 6", f"{stage} by function", values, table6.loc[stage].tolist())

dec = df[df.function == "Decision"]
check("4.2.3", "decision-dominant systems by Kautz type", "II: 4, III: 3, V: 1",
      ", ".join(f"{t}: {n}" for t, n in sorted(Counter(dec.kautz_type).items())))
check("4.2.3", "functions covered by Type III systems", 5, df[df.kautz_type == "III"].function.nunique())
abl = df.ablation_reported == "yes"
check("4.2.4", "studies reporting an ablation or component variant", 20, abl.sum())
check("4.2.4", "of these, with a control switching off the dominant symbolic operation", 11,
      (abl & (df.dominant_symbolic_operation_switched_off == "yes")).sum())

# --------------------------------------------------------------------------- RQ2
m = Counter(df.explanation_mode)
for mode, n in [("native", 5), ("trace", 3), ("score-only", 1), ("none", 18)]:
    check("4.3.1", f"explanation mode: {mode}", n, m[mode])
exposing = df[df.explanation_mode != "none"]
check("4.3.1", "studies exposing a pair-level justification that act at inference", 8, (exposing.stage == "N2").sum())
check("4.3.1", "...the only training-stage case", "KnowAug", ", ".join(exposing[exposing.stage == "N1"].system))
e = Counter(df.explanation_evaluation)
for ev, n in [("none", 20), ("example", 4), ("quantitative proxy", 3), ("user study", 0)]:
    check("4.3.2", f"explanation evaluation: {ev}", n, e[ev])
check("4.3.3", "studies with an implemented real-expert HITL loop", 0, (df.hitl_present == "yes").sum())
check("4.3.3", "studies reporting a human-effort measure", 0, (df.human_effort_reported == "yes").sum())
for col in ["expert_feedback_loop", "explanation_user_study", "human_effort_measure"]:
    check("4.3", f"negative audit, '{col}' found", 0, (audit[col] != "no").sum())

# --------------------------------------------------------------------------- RQ3
check("4.4.1", "EA/KG alignment or ontology matching/revision", 22,
      df.task_family.isin(["Entity and knowledge-graph alignment", "Ontology matching and revision"]).sum())
ml = Counter(df.multilingual_setting)
check("4.4.2", "benchmark multilinguality", 12, ml["benchmark"])
check("4.4.2", "not evaluated cross-lingually", 15, ml["none"])
check("4.4.2", "operational multilinguality", 0, ml["operational"])
check("4.4.3", "studies operationalising measurement information", "PhenoAlign, ReasonAlign",
      ", ".join(sorted(df[df.heterogeneity_measurement == "yes"].system)))

# --------------------------------------------------------------------------- Table A.1
TABLE_A1 = {  # system: (task family, Kautz, strategy, stage, function) as printed in the article
    "NeuSymEA": ("EA/KG", "V", "Logic", "N2*", "Decision"), "FLORA": ("EA/KG", "II", "Logic", "N2", "Decision"),
    "PRASE": ("EA/KG", "III", "Logic", "N2*", "Decision"), "NALA": ("EA/KG", "III", "Logic", "N2", "Decision"),
    "OntoEA": ("EA/KG", "V", "Logic", "N1", "Constr. enforcement"),
    "ESEA": ("EA/KG", "V", "Logic", "N1", "Constr. enforcement"),
    "CIDER-LM": ("EA/KG", "IV", "Logic", "N1*", "Constr. enforcement"),
    "PhenoAlign": ("EA/KG", "III", "Logic", "N2", "Decision"),
    "KnowAug": ("EA/KG", "IV", "Logic", "N1", "Cand. generation"),
    "LLM4EA": ("EA/KG", "IV", "Logic", "N1", "Constr. enforcement"),
    "CyberEA": ("EA/KG", "IV", "Logic", "N1", "Cand. generation"),
    "HSMGNN": ("EA/KG", "V", "Logic", "N1", "Constr. enforcement"),
    "SLHCat": ("EA/KG", "IV", "Structure", "N1", "Cand. generation"),
    "BERTMap": ("Ontology", "III", "Logic", "N2", "Repair"),
    "DAEOM": ("Ontology", "IV", "Structure", "N1", "Constr. enforcement"),
    "BioHAN": ("Ontology", "IV", "Logic", "N1", "Cand. generation"),
    "OntoConnect": ("Ontology", "IV", "Logic", "N1", "Cand. generation"),
    "DeepFCA": ("Ontology", "V", "Logic", "N1*", "Constr. enforcement"),
    "FCA-Map + SBERT": ("Ontology", "III", "Logic", "N2*", "Constr. enforcement"),
    "LogMap/AML + SiamNN": ("Ontology", "III", "Logic", "N2*", "Constr. enforcement"),
    "LogMap + LLM oracles": ("Ontology", "II", "Logic", "N2", "Decision"),
    "PLM ontology revision": ("Ontology", "II", "Logic", "N2", "Repair"),
    "SMoG": ("Schema", "III", "Structure", "N2", "Cand. generation"),
    "ReasonAlign": ("Schema", "II", "Logic", "N2", "Decision"),
    "MUT2KG": ("Schema", "V", "Logic", "N1", "Constr. enforcement"),
    "DMatch": ("ER", "II", "Logic", "N2", "Decision"),
    "HMatch": ("ER", "III", "Logic", "N2", "Explanation"),
}
FAMILY = {"Entity and knowledge-graph alignment": "EA/KG", "Ontology matching and revision": "Ontology",
          "Schema matching and data harmonization": "Schema", "Entity resolution and record matching": "ER"}
SHORT_FUNC = {"Candidate generation": "Cand. generation", "Constraint enforcement": "Constr. enforcement"}
a1 = pd.DataFrame({
    "system": df.system, "bibtex_key": df.bibtex_key, "task_family": df.task_family.map(FAMILY),
    "kautz": df.kautz_type, "strategy": df.strategy.str.replace("-based", "", regex=False),
    "stage": df.stage + df.mixed_stage.map({"yes": "*", "no": ""}),
    "function": df.function.replace(SHORT_FUNC),
})
a1.to_csv(RESULTS / "tableA1_included_studies.csv", index=False)
for _, r in a1.iterrows():
    check("Table A.1", r.system, TABLE_A1[r.system],
          (r.task_family, r.kautz, r.strategy, r.stage, r.function))


# --------------------------------------------------------------------------- evidence map figure
# Row labels exactly as printed in the evidence map of the article.
MAP_LABEL = {
    "LogMap/AML + SiamNN": "LogMap-ML (Chen 2021)", "PLM ontology revision": "Ji et al. 2023",
    "FCA-Map + SBERT": "FCA-Map (Li 2021)", "LogMap + LLM oracles": "Lushnei et al. 2025",
    "ESEA": "Jiang et al. 2022", "MUT2KG": "Mehryar et al. 2023",
}


def evidence_map(df):
    LABEL = {"Constraint enforcement": "Constr.", "Candidate generation": "Cand.", "Repair": "Repair",
             "Explanation": "Expl.", "Decision": "Decision"}
    d = pd.DataFrame({
        "label": [MAP_LABEL.get(s, f"{s} ({a} {y})") for s, a, y in zip(df.system, df.first_author, df.year_assessed)],
        "family": df.task_family, "kautz": df.kautz_type,
        "d3": df.strategy.map({"Logic-based": "Logic", "Structure-based": "Struct."}),
        "locus": df.stage, "d5": df.function.map(LABEL),
        "expl": df.explanation_mode.map({"none": "None", "score-only": "Score", "trace": "Trace", "native": "Native"}),
        "eval": df.explanation_evaluation.map({"none": "None", "example": "Example",
                                               "quantitative proxy": "Proxy", "user study": "User"}),
        "hitl": df.hitl_present.map({"no": "No", "yes": "Yes"}),
        "year": df.year_assessed.astype(int),
    })
    families = list(FAMILY)
    order = ["Cand.", "Constr.", "Repair", "Expl.", "Decision"]
    d["fam_i"], d["d5_i"] = d.family.map(families.index), d.d5.map(order.index)
    d = d.sort_values(["fam_i", "locus", "d5_i", "year", "label"])

    def tint(hex_, a=0.38):
        rgb = [int(hex_[i:i + 2], 16) for i in (1, 3, 5)]
        return "#" + "".join(f"{round(255 - a * (255 - c)):02x}" for c in rgb)

    fill = {"N1": tint("#2a78d6"), "N2": tint("#eb6834"), "Cand.": tint("#1baf7a"), "Constr.": tint("#eda100"),
            "Repair": tint("#e87ba4"), "Expl.": tint("#008300"), "Decision": tint("#6250d6")}
    INK, MUTED, RULE, BAND = "#0b0b0b", "#8a8986", "#d9d8d4", "#f2f1ee"
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 6.6, "pdf.fonttype": 42})
    cols = [("label", "Study", 1.95, "left"), ("kautz", "Kautz", 0.48, "center"),
            ("d3", "Strategy", 0.58, "center"), ("locus", "Stage", 0.50, "center"),
            ("d5", "Function", 0.70, "center"), (None, "", 0.14, None),
            ("expl", "Explanation", 0.74, "center"), ("eval", "Evaluation", 0.74, "center"),
            ("hitl", "HITL", 0.50, "center")]
    x = [0.0]
    for c in cols:
        x.append(x[-1] + c[2])
    W, RH, FH, HH, TL = x[-1], 0.158, 0.19, 0.20, 0.15
    H = 2 * HH + len(families) * FH + len(d) * RH + 0.10 + 5 * TL + 0.10
    fig = plt.figure(figsize=(W + 0.3, H + 0.05))
    ax = fig.add_axes([0.05 / (W + 0.3), 0.0, W / (W + 0.3), H / (H + 0.05)])
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.axis("off")
    cx = lambda i: (x[i] + x[i + 1]) / 2

    y = 0.0
    for a, b, text in [(x[1], x[5], "C1 · Architecture and symbolic participation"),
                       (x[6], x[9], "C2 · Explanation and human validation")]:
        ax.text((a + b) / 2, y + HH / 2, text, ha="center", va="center", fontweight="bold", color=INK)
        ax.plot([a + 0.03, b - 0.03], [y + HH - 0.02] * 2, color=INK, lw=0.6)
    y += HH
    for i, (key, title, w, al) in enumerate(cols):
        if key:
            ax.text(x[i] + 0.04 if al == "left" else cx(i), y + HH / 2, title, ha=al, va="center",
                    fontweight="bold", color=INK)
    y += HH
    ax.plot([0, W], [y, y], color=INK, lw=0.8)
    for f_i, fam in enumerate(families):
        sub = d[d.fam_i == f_i]
        ax.add_patch(Rectangle((0, y), W, FH, color=BAND, lw=0))
        ax.text(0.04, y + FH / 2, f"{fam} (n = {len(sub)})", ha="left", va="center", fontstyle="italic", color=INK)
        y += FH
        for _, r in sub.iterrows():
            for i, (key, title, w, al) in enumerate(cols):
                if not key:
                    continue
                val = r[key]
                if key in ("locus", "d5"):
                    ax.add_patch(Rectangle((x[i] + 0.025, y + 0.012), w - 0.05, RH - 0.024, color=fill[val], lw=0))
                muted = val in ("None", "No")
                ax.text(x[i] + 0.04 if al == "left" else cx(i), y + RH / 2, val, ha=al, va="center",
                        color=MUTED if muted else INK,
                        fontweight="bold" if key in ("expl", "eval", "hitl") and not muted else "normal")
            y += RH
            ax.plot([0, W], [y, y], color=RULE, lw=0.35)
    ax.plot([(x[5] + x[6]) / 2] * 2, [HH, y], color=INK, lw=0.8)
    ax.plot([0, W], [y, y], color=INK, lw=0.8)
    totals = {"kautz": ["II", "III", "IV", "V"], "d3": ["Logic", "Struct."], "locus": ["N1", "N2"],
              "d5": order, "expl": ["Native", "Trace", "Score", "None"],
              "eval": ["User", "Example", "Proxy", "None"], "hitl": ["Yes", "No"]}
    ax.add_patch(Rectangle((0, y), W, 0.10 + 5 * TL + 0.04, color=BAND, lw=0))
    y += 0.10
    ax.text(0.04, y + TL / 2, f"Total (N = {len(d)})", ha="left", va="center", fontweight="bold", color=INK)
    for i, (key, *_rest) in enumerate(cols):
        if key in totals:
            cnt = Counter(d[key])
            for j, cat in enumerate(totals[key]):
                yy = y + (j + 0.5) * TL
                ax.text(cx(i) + 0.05, yy, cat, ha="right", va="center", color=INK, fontsize=6.8)
                ax.text(cx(i) + 0.10, yy, str(cnt.get(cat, 0)), ha="left", va="center", color=INK,
                        fontsize=6.8, fontweight="bold")
    fig.savefig(FIGURES / "evidence_map.pdf")
    fig.savefig(FIGURES / "evidence_map.png", dpi=220)
    plt.close(fig)


if __name__ == "__main__":
    RESULTS.mkdir(exist_ok=True)
    FIGURES.mkdir(exist_ok=True)
    evidence_map(df)
    out = pd.DataFrame(checks)
    out.to_csv(RESULTS / "article_checks.csv", index=False)
    pd.set_option("display.width", 200)
    pd.set_option("display.max_colwidth", 70)
    print(out.to_string(index=False))
    print(f"\n{(out.match == 'yes').sum()} of {len(out)} reported values reproduced.")
    print("\nFull-text exclusions by recorded basis:")
    print(reasons.to_string(index=False))
