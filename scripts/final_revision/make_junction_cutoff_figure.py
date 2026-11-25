"""Regenerate the fixed-cutoff and descriptive log-fit junction figure.

All inputs are archived diagnostics; no new simulation is performed.  The plot
is deliberately descriptive: a high R2 for D(N)=a+b ln N over three grids does
not establish an asymptotic law, and a physical cutoff r0 does not establish a
grid-independent full-domain dissipation.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
V2 = ROOT / "06_physics" / "results_jonction_v2"
J = ROOT / "06_physics" / "results_jonction"
OUTS = [
    ROOT / "08_operator_results" / "PH13_manuscript" / "submission_package" / "figs_new",
    ROOT / "corrections for reviewer" / "PH13_revision_data" / "figures" / "final_supplement",
]

summary = json.loads((V2 / "A1v2_summary.json").read_text(encoding="utf-8"))
fit = json.loads((J / "jonction_fit.json").read_text(encoding="utf-8"))

with (ROOT / "corrections for reviewer" / "PH13_revision_data" / "data" / "junction"
      / "junction_budget.csv").open(newline="", encoding="utf-8") as fh:
    budget = list(csv.DictReader(fh))

r0 = np.asarray(summary["r0"], float)
keys30 = ["r0", "r0.125", "r0.25", "r0.5"]
labels = ["0", "0.125", "0.25", "0.5"]
pct = np.array([
    [summary["cases30"][k]["median_pct"] for k in keys30],
    [summary["cases30"][k]["min_pct"] for k in keys30],
    [summary["cases30"][k]["max_pct"] for k in keys30],
])

fig, axes = plt.subplots(1, 3, figsize=(14.2, 4.3))
ax = axes[0]
ax.fill_between(r0, pct[1], pct[2], color="#dce6f2", label="30-case min--max")
ax.plot(r0, pct[0], "o-", color="#1f4e79", lw=1.8, label="30-case median")
for key, marker, colour in [("n1.25_Re300", "s", "#b22222"),
                            ("n3.0_Re1000", "^", "#2e8b57"),
                            ("n8.0_Re1000", "d", "#8b4513")]:
    vals = [100 * summary["series"][key][k]["var_128_256"]
            for k in keys30]
    ax.plot(r0, vals, marker + "--", color=colour, ms=4.5, lw=1.0,
            label=key.replace("_", " "))
ax.set_xlabel(r"fixed physical cutoff $r_0$")
ax.set_ylabel(r"$D_{256}/D_{128}-1$ (%)")
ax.set_title("(a) Fixed-wall-cutoff comparison")
ax.grid(alpha=0.25)
ax.legend(fontsize=7, loc="upper right")

ax = axes[1]
selected = [
    ("se_n4p0_Re1000_N128", "n=4, Re=1000, N=128", "o"),
    ("se_n4p0_Re1000_N256", "n=4, Re=1000, N=256", "s"),
    ("se_n8p0_Re1000_N128", "n=8, Re=1000, N=128", "^"),
]
for cid, label, marker in selected:
    rows = sorted([r for r in budget if r["case_id"] == cid],
                  key=lambda r: float(r["r_physical"]))
    N = int(rows[0]["N"])
    h = 2.0 / (N - 1)
    x = np.log(np.array([float(r["r_physical"]) / h for r in rows]))
    y = np.array([float(r["D_junction"]) for r in rows])
    ax.plot(x, y, marker + "-", lw=1.6, ms=5, label=label)
ax.set_xlabel(r"$\ln(r/h)$")
ax.set_ylabel(r"$D_{\rm junction}(r,N)$")
ax.set_title("(b) Junction contribution versus cutoff")
ax.grid(alpha=0.25)
ax.legend(fontsize=7, loc="upper left")

ax = axes[2]
Ns = np.array([64.0, 128.0, 256.0])
ns = np.array([1.25, 3.0, 8.0])
colours = ["#b22222", "#2e8b57", "#1f4e79"]
series_names = ["n1.25_Re300", "n3.0_Re1000", "n8.0_Re1000"]
for name, nval, colour in zip(series_names, ns, colours):
    for kind, style, width in [("D_total", "-", 1.8), ("D_excl_16h", "--", 1.2)]:
        p = fit["series"][name][kind]
        y = p["a"] + p["b"] * np.log(Ns)
        ax.plot(np.log(Ns), y, style, color=colour, lw=width,
                label=f"n={nval:g}, " + ("total" if kind == "D_total" else "r0=0.5"))
        ax.plot(np.log(Ns), y, "o" if kind == "D_total" else "s",
                color=colour, ms=4)
ax.set_xlabel(r"$\ln N$")
ax.set_ylabel(r"$D(N)$")
ax.set_title(r"(c) Descriptive fits $D=a+b\ln N$")
ax.grid(alpha=0.25)
ax.legend(fontsize=6.5, loc="upper left", ncol=2)

fig.suptitle("Junction cutoff diagnostics (descriptive; not grid-independent dissipation)",
             fontsize=10.5)
fig.tight_layout(rect=(0, 0, 1, 0.93))
for out in OUTS:
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / "fig_junction_cutoffs.png", dpi=320, bbox_inches="tight")
    fig.savefig(out / "fig_junction_cutoffs.pdf", bbox_inches="tight")
    print("wrote", out / "fig_junction_cutoffs.png")

# LaTeX fragments -----------------------------------------------------------
lines = [r"\begin{tabular}{@{}lrrr@{}}", r"\toprule",
         r"$r_0$ & median (\%) & min (\%) & max (\%) \\", r"\midrule"]
for k, lab in zip(keys30, labels):
    c = summary["cases30"][k]
    lines.append(f"{lab} & {c['median_pct']:.2f} & {c['min_pct']:.2f} & {c['max_pct']:.2f} \\\\")
lines += [r"\bottomrule", r"\end{tabular}"]
(V2 / "junction_cutoff_table.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")

lines = [r"\begin{tabular}{@{}llrrr@{}}", r"\toprule",
         r"case & support & $a$ & $b$ & $R^2$ \\", r"\midrule"]
for name, nval in zip(series_names, ns):
    Re = 300 if nval == 1.25 else 1000
    for kind, lab in [("D_total", "total"), ("D_excl_16h", r"$r_0=0.5$")]:
        p = fit["series"][name][kind]
        lines.append(f"$n={nval:g}, Re={Re}$ & {lab} & "
                     f"{p['a']:.6f} & {p['b']:.6f} & {p['R2']:.4f} \\\\")
lines += [r"\bottomrule", r"\end{tabular}"]
(V2 / "junction_logfit_table.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("wrote LaTeX table fragments")
