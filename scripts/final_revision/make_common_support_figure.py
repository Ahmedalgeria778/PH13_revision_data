"""Regenerate the common-support LBM/FEM dissipation figure from the CSV."""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
CSV = ROOT / "corrections for reviewer" / "PH13_revision_data" / "data" / "final_revision" / "common_support_dissipation.csv"
OUTS = [
    ROOT / "08_operator_results" / "PH13_manuscript" / "submission_package" / "figs_new",
    ROOT / "corrections for reviewer" / "PH13_revision_data" / "figures" / "final_supplement",
]

with CSV.open(newline="", encoding="utf-8") as fh:
    rows = list(csv.DictReader(fh))

labels = [f"$n={float(r['n']):g}$\n$Re={int(float(r['Re']))}$" for r in rows]
x = np.arange(len(rows))
w = 0.26
lbm = np.array([float(r["D_LBM_M"]) for r in rows])
fem_m = np.array([float(r["D_FEM_M"]) for r in rows])
fem_o = np.array([float(r["D_FEM_Omega"]) for r in rows])
eps = np.array([float(r["eps_D_percent"]) for r in rows])

fig, (ax, ax2) = plt.subplots(2, 1, figsize=(9.6, 6.6), sharex=True,
                              gridspec_kw={"height_ratios": [3, 1.4]})
# Grayscale-safe bars: fill level and hatch both encode the series.
ax.bar(x - w, lbm, w, label=r"$D_{\rm LBM}^{M}$", color="0.82",
       edgecolor="k", linewidth=0.8, hatch="//")
ax.bar(x, fem_m, w, label=r"$D_{\rm FEM}^{M}$", color="white",
       edgecolor="k", linewidth=0.8, hatch="..")
ax.bar(x + w, fem_o, w, label=r"$D_{\rm FEM}^{\Omega}$", color="0.45",
       edgecolor="k", linewidth=0.8, hatch="\\\\")
ax.set_ylabel("dissipation $D$")
ax.set_title("Common-support dissipation and full-domain FEM support effect")
ax.grid(axis="y", alpha=0.25)
ax.legend(fontsize=9, ncol=3)

ax2.bar(x, eps, 0.5, color="white", edgecolor="k", linewidth=0.8, hatch="xx")
for i, value in enumerate(eps):
    ax2.text(i, value + 0.12, f"{value:.2f}%", ha="center", fontsize=7.5)
ax2.set_ylabel(r"$\varepsilon_D$ (%)")
ax2.set_xlabel("common-support case")
ax2.set_xticks(x, labels, fontsize=8)
ax2.grid(axis="y", alpha=0.25)
ax2.set_ylim(0, max(eps) * 1.25)
fig.tight_layout()
for out in OUTS:
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / "fig_supp_common_support_dissipation.png", dpi=320,
                bbox_inches="tight")
    fig.savefig(out / "fig_supp_common_support_dissipation.pdf",
                bbox_inches="tight")
    print("wrote", out / "fig_supp_common_support_dissipation.png")
