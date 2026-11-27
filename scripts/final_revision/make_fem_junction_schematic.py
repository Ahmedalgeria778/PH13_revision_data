"""Regenerate the FEM tangential-lid junction schematic in print-safe style.

The moving upper arc is solid and carries a filled-circle junction marker; the
fixed lower arc is dashed and carries an open-square marker.  Shape and line
style, not colour, encode the assignment.  The symbol definitions are placed in
a separate footer legend so that they cannot overlap the junction annotations
or the arc labels in the typeset PDF.  The tiny left-junction ordinate is the
archived machine-precision value rounded to two significant figures.
"""
from __future__ import annotations

import math
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
TARGET_SIZE = (1343, 978)  # archived dimensions; keeps the typeset float unchanged


def match_archived_size(path, size):
    """Restore the archived raster dimensions without cropping any content."""
    image = Image.open(path).convert("RGB")
    if image.size == size:
        return
    ratio = image.width / image.height
    target_ratio = size[0] / size[1]
    if abs(ratio - target_ratio) < 0.05:
        image.resize(size, Image.Resampling.LANCZOS).save(path)
        return
    scale = max(image.width / size[0], image.height / size[1])
    canvas_size = (math.ceil(size[0] * scale), math.ceil(size[1] * scale))
    canvas = Image.new("RGB", canvas_size, "white")
    canvas.paste(image, ((canvas_size[0] - image.width) // 2,
                         (canvas_size[1] - image.height) // 2))
    canvas.resize(size, Image.Resampling.LANCZOS).save(path)


theta_up = np.linspace(0, np.pi, 400)
theta_down = np.linspace(np.pi, 2 * np.pi, 400)
x_up, y_up = np.cos(theta_up), np.sin(theta_up)
x_down, y_down = np.cos(theta_down), np.sin(theta_down)

fig, ax = plt.subplots(figsize=(8.4, 5.0))
fig.subplots_adjust(left=0.03, right=0.97, top=0.90, bottom=0.24)

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

# Junction annotations are kept outside the circle: left text grows to the
# left, right text grows to the right, so neither leader crosses the drawing.
ax.annotate(r"left junction: $y=+1.2\times10^{-16}$" "\n(moving by $y>0$)",
            xy=(-1, 0), xytext=(-1.28, -0.48), fontsize=10.5, ha="right",
            va="center",
            arrowprops=dict(arrowstyle="->", color="0.25", lw=1.0))
ax.annotate(r"right junction: $y=0$" "\n(fixed by $y>0$)",
            xy=(1, 0), xytext=(1.28, -0.48), fontsize=10.5, ha="left",
            va="center",
            arrowprops=dict(arrowstyle="->", color="0.25", lw=1.0))

ax.text(0, 1.20, "moving upper arc", ha="center", va="bottom", fontsize=11.5)
ax.text(0, -1.20, "fixed lower arc", ha="center", va="top", fontsize=11.5)

handles = [
    Line2D([], [], color="k", lw=2.4, label="moving arc (solid)"),
    Line2D([], [], color="k", lw=1.8, linestyle=(0, (6, 4)),
           label="fixed arc (dashed)"),
    Line2D([], [], color="k", marker="o", ms=7, linestyle="None",
           label=r"left: filled circle, $y>0$"),
    Line2D([], [], color="k", marker="s", ms=7, mfc="white", mew=1.5,
           linestyle="None", label=r"right: open square, $y=0$"),
]
fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 0.025),
           ncol=2, fontsize=10.5, frameon=False, handlelength=2.6,
           columnspacing=2.0, borderaxespad=0.0)

ax.set_aspect("equal", adjustable="box")
ax.set_xlim(-2.7, 2.7)
ax.set_ylim(-1.45, 1.45)
ax.axis("off")
ax.set_title("Tangential-lid junction convention", fontsize=13, pad=10)

for out in OUTS:
    out.mkdir(parents=True, exist_ok=True)
    target = out / NAME
    fig.savefig(target, dpi=220, bbox_inches="tight")
    match_archived_size(target, TARGET_SIZE)
    print("wrote", target, Image.open(target).size)
plt.close(fig)
