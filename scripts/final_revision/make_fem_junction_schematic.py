"""Regenerate the FEM tangential-lid junction schematic in print-safe style.

The moving upper arc is solid and carries filled-circle junction markers; the
fixed lower arc is dashed and carries an open-square marker.  Shape and line
style, not colour, encode the assignment.  The tiny left-junction ordinate is
the archived machine-precision value rounded to two significant figures.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from PIL import Image

ROOT = Path(__file__).resolve().parents[4]
OUTS = [
    ROOT / "08_operator_results" / "PH13_manuscript" / "submission_package" / "figs_new",
    ROOT / "08_operator_results" / "PH13_manuscript" / "submission_package" / "figs",
    ROOT / "corrections for reviewer" / "PH13_revision_data" / "figures" / "final_supplement",
    ROOT / "corrections for reviewer" / "PH13_revision_data" / "supplement" / "figs_new",
    ROOT / "corrections for reviewer" / "PH13_revision_data" / "supplement" / "figs",
]
NAME = "fig_supp_fem_junction_schematic.png"
TARGET_ASPECT = 1343 / 978  # archived aspect; keeps the typeset float unchanged


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


theta_up = np.linspace(0, np.pi, 400)
theta_down = np.linspace(np.pi, 2 * np.pi, 400)
x_up, y_up = np.cos(theta_up), np.sin(theta_up)
x_down, y_down = np.cos(theta_down), np.sin(theta_down)

fig, ax = plt.subplots(figsize=(7.2, 5.0), constrained_layout=True)
ax.plot(x_up, y_up, color="k", lw=2.4, solid_capstyle="round")
ax.plot(x_down, y_down, color="k", lw=1.8, linestyle=(0, (6, 4)),
        solid_capstyle="round")

# Direction of the tangential law u_w = U_lid (n_y, -n_x): clockwise on the
# upper arc, i.e. from the left junction towards the right junction.
for a in (2.45, 1.75, 1.05, 0.35):
    p = np.array([np.cos(a), np.sin(a)])
    tangent = np.array([np.sin(a), -np.cos(a)])
    ax.annotate("", xy=p + 0.105 * tangent, xytext=p - 0.105 * tangent,
                arrowprops=dict(arrowstyle="-|>", color="k", lw=1.4,
                                mutation_scale=12))

# FEM nodal assignment by the strict y > 0 test.
ax.plot([-1], [0], marker="o", ms=9, mfc="k", mec="k", linestyle="None", zorder=5)
ax.plot([1], [0], marker="s", ms=9, mfc="white", mec="k", mew=1.8,
        linestyle="None", zorder=5)

ax.annotate(r"left junction: $y=+1.2\times10^{-16}$" "\n(moving by $y>0$)",
            xy=(-1, 0), xytext=(-1.42, -0.45), fontsize=10, ha="left",
            arrowprops=dict(arrowstyle="->", color="0.25", lw=1.0))
ax.annotate(r"right junction: $y=0$" "\n(fixed by $y>0$)",
            xy=(1, 0), xytext=(1.42, -0.45), fontsize=10, ha="right",
            arrowprops=dict(arrowstyle="->", color="0.25", lw=1.0))
ax.text(0, 1.22, "moving upper arc", ha="center", fontsize=11)
ax.text(0, -1.25, "fixed lower arc", ha="center", fontsize=11)

handles = [
    Line2D([], [], color="k", lw=2.4, label="moving arc"),
    Line2D([], [], color="k", lw=1.8, linestyle=(0, (6, 4)), label="fixed arc"),
    Line2D([], [], color="k", marker="o", ms=7, linestyle="None",
           label=r"left: $y>0$"),
    Line2D([], [], color="k", marker="s", ms=7, mfc="white", mew=1.5,
           linestyle="None", label=r"right: $y=0$"),
]
ax.legend(handles=handles, fontsize=9, frameon=False, loc="lower center",
          ncol=2)
ax.set_aspect("equal", adjustable="box")
ax.set_xlim(-1.55, 1.55)
ax.set_ylim(-1.45, 1.45)
ax.axis("off")
ax.set_title("Tangential-lid junction convention", fontsize=12)

for out in OUTS:
    out.mkdir(parents=True, exist_ok=True)
    target = out / NAME
    fig.savefig(target, dpi=220, bbox_inches="tight")
    pad_to_aspect(target, TARGET_ASPECT)
    print("wrote", target)
plt.close(fig)
