"""Regenerate the supplementary wall/core split figure from the archived CSV.

Marker shape identifies the contribution (total, wall or core) and line style
identifies the wall-band thickness, so the six series remain distinguishable in
black-and-white print.  No value is typed by hand and no diagnostic is changed.
"""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

ROOT = Path(__file__).resolve().parents[4]
CSV = ROOT / "corrections for reviewer" / "PH13_revision_data" / "data" / "core_wall" / "core_wall_budget.csv"
OUTS = [
    ROOT / "08_operator_results" / "PH13_manuscript" / "submission_package" / "figs_new",
    ROOT / "08_operator_results" / "PH13_manuscript" / "submission_package" / "figs",
    ROOT / "corrections for reviewer" / "PH13_revision_data" / "figures" / "final_supplement",
    ROOT / "corrections for reviewer" / "PH13_revision_data" / "supplement" / "figs_new",
    ROOT / "corrections for reviewer" / "PH13_revision_data" / "supplement" / "figs",
]
NAME = "fig_supp_corewall_Re100_500_1000.png"
TARGET_ASPECT = 3278 / 830  # archived aspect; keeps the typeset float unchanged


def pad_to_aspect(path, aspect):
    """Add white side margins without altering any plotted content."""
    image = Image.open(path).convert("RGB")
    width, height = image.size
    target_width = int(round(height * aspect))
    if target_width <= width:
        return
    canvas = Image.new("RGB", (target_width, height), "white")
    canvas.paste(image, ((target_width - width) // 2, 0))
    canvas.save(path)


with CSV.open(newline="", encoding="utf-8") as fh:
    rows = list(csv.DictReader(fh))

RES = (100.0, 500.0, 1000.0)
QUANTITIES = (
    ("Dmask_over_A", "total", "o"),
    ("Dwall_over_A", "wall", "s"),
    ("Dcore_over_A", "core", "^"),
)
DELTAS = ((0.025, "-"), (0.05, "--"))

fig, axes = plt.subplots(1, 3, figsize=(13.2, 3.5), sharex=True, sharey=True)
for ax, Re in zip(axes, RES):
    for delta, ls in DELTAS:
        sub = sorted(
            (
                r for r in rows
                if float(r["Re"]) == Re
                and int(r["N"]) == 128
                and abs(float(r["delta_over_Lc"]) - delta) < 1e-12
            ),
            key=lambda r: float(r["n"]),
        )
        if not sub:
            raise SystemExit(f"no rows for Re={Re:g}, delta={delta}")
        x = [float(r["n"]) for r in sub]
        for key, label, marker in QUANTITIES:
            y = [float(r[key]) for r in sub]
            dlab = r"$\delta=0.025L_c$" if delta == 0.025 else r"$\delta=0.05L_c$"
            ax.plot(x, y, color="k", marker=marker, linestyle=ls, lw=1.2, ms=4,
                    label=f"{label}, {dlab}")
    ax.set_title(f"Re = {Re:g}, N = 128", fontsize=11)
    ax.set_xlabel(r"$n$", fontsize=11)
    ax.grid(alpha=0.25)
    ax.tick_params(labelsize=9)

axes[0].set_ylabel(r"contribution / $A_{\rm mask}$", fontsize=11)
axes[0].legend(fontsize=6.8, frameon=False, ncol=2, loc="best")
fig.suptitle("Wall and core contributions on the fixed-resolution reference grid",
             fontsize=12)
fig.tight_layout(rect=(0, 0, 1, 0.91))
for out in OUTS:
    out.mkdir(parents=True, exist_ok=True)
    target = out / NAME
    fig.savefig(target, dpi=250, bbox_inches="tight")
    pad_to_aspect(target, TARGET_ASPECT)
    print("wrote", target)
plt.close(fig)
