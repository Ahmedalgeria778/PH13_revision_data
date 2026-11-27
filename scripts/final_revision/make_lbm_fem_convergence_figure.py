"""Regenerate the LBM--FEM convergence panel from the archived CSV.

The left panel is the spatial sensitivity check used in the supplement; the
right panel is the fixed-resolution Mach-dependence control already present in
the archived figure.  All series use distinct black line styles and markers,
so neither panel relies on colour to identify its curves.
"""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
CSV = ROOT / "04_reference_FEM" / "validation" / "results" / "lbm_vs_fem_convergence" / "convergence.csv"
OUTS = [
    ROOT / "08_operator_results" / "PH13_manuscript" / "submission_package" / "figs_new",
    ROOT / "08_operator_results" / "PH13_manuscript" / "submission_package" / "figs",
    ROOT / "corrections for reviewer" / "PH13_revision_data" / "figures" / "final_supplement",
    ROOT / "corrections for reviewer" / "PH13_revision_data" / "figures",
    ROOT / "corrections for reviewer" / "PH13_revision_data" / "supplement" / "figs_new",
    ROOT / "corrections for reviewer" / "PH13_revision_data" / "supplement" / "figs",
]
NAME = "figS11b_lbm_fem_convergence_N.png"

text = CSV.read_text(encoding="utf-8")
spatial_text, mach_text = text.split("\n\n", 1)
spatial = list(csv.DictReader(spatial_text.splitlines()))
mach = list(csv.DictReader(mach_text.splitlines()))

Ns = np.array([float(r["N"]) for r in spatial])
l2 = np.array([float(r["l2_int"]) for r in spatial])
dU = np.array([abs(0.05 - float(r["U"])) for r in mach])
l2u = np.array([float(r["l2_int"]) for r in mach])
mask = dU > 0

fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))
ax = axes[0]
ax.loglog(Ns, l2, color="k", marker="o", linestyle="-", lw=1.6, ms=5,
          label="LBM vs FEM")
ax.loglog(Ns, l2[0] * Ns[0] / Ns, color="k", linestyle="--", lw=1.3,
          label=r"$O(h)$")
ax.loglog(Ns, l2[0] * (Ns[0] / Ns) ** 2, color="k", linestyle=":", lw=1.5,
          label=r"$O(h^2)$")
ax.set_xlabel(r"$N$ (LBM)")
ax.set_ylabel(r"interior $L_2$ discrepancy")
ax.set_title("(a) Spatial convergence (circle, Re = 100)")
ax.grid(True, which="both", alpha=0.3)
ax.legend(fontsize=9, frameon=False)

ax = axes[1]
ax.loglog(dU[mask], l2u[mask], color="k", marker="s", linestyle="-", lw=1.6,
          ms=5, label="LBM(U) vs LBM(0.05)")
c = l2u[mask][0] / dU[mask][0]
ax.loglog(dU[mask], c * dU[mask], color="k", linestyle="--", lw=1.3,
          label=r"$O(|U-0.05|)$")
ax.set_xlabel(r"$|U-0.05|$ (Mach control)")
ax.set_ylabel(r"interior $L_2$ discrepancy")
ax.set_title("(b) Mach-dependence control (N = 64)")
ax.grid(True, which="both", alpha=0.3)
ax.legend(fontsize=9, frameon=False)

fig.tight_layout()
for out in OUTS:
    out.mkdir(parents=True, exist_ok=True)
    target = out / NAME
    fig.savefig(target, dpi=140)
    print("wrote", target)
plt.close(fig)
