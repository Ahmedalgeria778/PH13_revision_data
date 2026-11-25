# -*- coding: utf-8 -*-
"""Figures for the final physics-only manuscript and its supplement.

All quantitative panels are generated from the CSVs produced by the executed
correction scripts in ../01..05. No numeric value is typed by hand.
"""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent
FIG = OUT / "figs_new"
FIG.mkdir(parents=True, exist_ok=True)
BASE = OUT.parent


def readcsv(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def arrow(x, y, ax, fmt="%.3f"):
    order = np.argsort(x)
    x, y = np.asarray(x)[order], np.asarray(y)[order]
    ax.plot(x, y, "o-", ms=4)
    for xi, yi in zip(x, y):
        ax.annotate(fmt % yi, (xi, yi), textcoords="offset points",
                    xytext=(0, 5), fontsize=7, ha="center")


def fig_budget():
    rows = readcsv(BASE / "04_additive_core_wall_budget" / "core_wall_budget.csv")
    fig, axes = plt.subplots(1, 3, figsize=(11.2, 3.5), sharex=True, sharey=True)
    for ax, Re in zip(axes, (300.0, 500.0, 1000.0)):
        sub = [r for r in rows if float(r["Re"]) == Re and int(r["N"]) == 256
               and abs(float(r["delta_over_Lc"]) - 0.05) < 1e-12]
        sub.sort(key=lambda r: float(r["n"]))
        n = [float(r["n"]) for r in sub]
        ax.plot(n, [float(r["Dmask_over_A"]) for r in sub], "k-o", lw=1.8,
                label=r"$D/A_{\rm mask}$")
        ax.plot(n, [float(r["Dwall_over_A"]) for r in sub], "s--", ms=4,
                label=r"$D_{\rm wall}/A_{\rm mask}$")
        ax.plot(n, [float(r["Dcore_over_A"]) for r in sub], "^--", ms=4,
                label=r"$D_{\rm core}/A_{\rm mask}$")
        ax.set_title(r"$Re=%d,\ N=256$" % Re)
        ax.set_xlabel(r"$n$")
        ax.grid(alpha=0.3)
    axes[0].set_ylabel(r"dissipation per unit $A_{\rm mask}$")
    axes[0].legend(fontsize=7, loc="best")
    fig.suptitle("Additive core/wall budget: the rise beyond the low-loss band is core-driven",
                 fontsize=10)
    fig.tight_layout()
    fig.savefig(FIG / "fig_core_wall_budget.png", dpi=200)
    plt.close(fig)


def fig_junction():
    rows = readcsv(BASE / "02_junction_energy_budget" / "junction_budget.csv")
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.5), sharey=True)
    for ax, Re in zip(axes, (100.0, 1000.0)):
        for n in (1.25, 2.0, 4.0, 8.0):
            sub = [r for r in rows if float(r["Re"]) == Re and abs(float(r["n"]) - n) < 1e-9]
            sub.sort(key=lambda r: float(r["r_over_Lc"]))
            ax.plot([float(r["r_over_Lc"]) for r in sub],
                    [100 * float(r["f_junction"]) for r in sub], "o-",
                    ms=4, label=r"$n=%g$" % n)
        ax.set_title(r"$Re=%d$" % Re)
        ax.set_xlabel(r"excision radius $r/L_c$")
        ax.grid(alpha=0.3)
    axes[0].set_ylabel(r"$100\,D_{\rm junction}/D_{\rm mask}$  [\%]")
    axes[0].legend(fontsize=8)
    fig.suptitle("Dissipation inside the two tangential-lid junction disks", fontsize=10)
    fig.tight_layout()
    fig.savefig(FIG / "fig_junction_share.png", dpi=200)
    plt.close(fig)


def fig_dissipation():
    """Figure 2 panels: simplified curve legend and horizontal map ticks."""
    rows = readcsv(Path(r"C:\Users\user\Documents\Default Project\GIRVD (revised)")
                   / "06_physics" / "results_190" / "physics_observables.csv")
    res = sorted({float(r["Re"]) for r in rows})
    highlighted = (100.0, 300.0, 500.0, 1000.0)
    colors = {100.0: "#2b6cb0", 300.0: "#2f855a", 500.0: "#c05621", 1000.0: "#6b46c1"}

    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    for Re in res:
        sub = sorted((r for r in rows if abs(float(r["Re"]) - Re) < 1e-9),
                     key=lambda r: float(r["n"]))
        n = [float(r["n"]) for r in sub]
        d = [float(r["dissipation"]) for r in sub]
        if Re in highlighted:
            ax.plot(n, d, "o-", ms=4.5, lw=1.8, color=colors[Re], label=r"$Re=%d$" % Re)
        else:
            ax.plot(n, d, "-", lw=0.8, color="0.78", zorder=0)
    ax.set_xlabel("superellipse exponent $n$", fontsize=11)
    ax.set_ylabel("integrated dissipation $D$", fontsize=11)
    ax.tick_params(labelsize=10)
    ax.grid(alpha=0.25)
    ax.legend(fontsize=9, frameon=False, ncol=2, loc="best")
    fig.tight_layout()
    fig.savefig(FIG / "curve_dissipation_vs_n.png", dpi=220)
    plt.close(fig)

    ns = sorted({float(r["n"]) for r in rows})
    values = np.full((len(res), len(ns)), np.nan)
    n_index = {n: j for j, n in enumerate(ns)}
    r_index = {r: i for i, r in enumerate(res)}
    for r in rows:
        values[r_index[float(r["Re"])], n_index[float(r["n"])]] = (
            float(r["dissipation"]) / float(r["area_mask"]))

    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    image = ax.imshow(values, origin="lower", aspect="auto", interpolation="nearest",
                      extent=[min(ns), max(ns), min(res), max(res)])
    fig.colorbar(image, ax=ax, label=r"$D/A_{\rm mask}$")
    ax.set_xlabel("superellipse exponent $n$", fontsize=11)
    ax.set_ylabel("Reynolds number $Re$", fontsize=11)
    ax.tick_params(labelsize=10)
    ax.set_xticks(ns)
    ax.set_yticks([100, 200, 300, 400, 500, 600, 700, 800, 900, 1000])
    fig.tight_layout()
    fig.savefig(FIG / "map_dissipation.png", dpi=220)
    plt.close(fig)


def fig_fields_plate():
    """Stack the four native field plates so each panel is about twice as wide."""
    names = ["se_n1p25_Re1000_N128_fields.png", "se_n2p0_Re1000_N128_fields.png",
             "se_n4p0_Re1000_N128_fields.png", "se_n8p0_Re1000_N128_fields.png"]
    labels = [r"$n=1.25$", r"$n=2$", r"$n=4$", r"$n=8$"]
    src = FIG.parent / "figs"
    ims = [Image.open(src / name).convert("RGB") for name in names]
    width = max(im.width for im in ims)
    header, gap, margin = 34, 12, 8
    height = sum(im.height + header + gap for im in ims) + gap
    canvas = Image.new("RGB", (width + 2 * margin, height), "white")
    draw = ImageDraw.Draw(canvas)
    y = gap
    for im, label in zip(ims, labels):
        draw.text((margin, y + 8), label, fill="black")
        y += header
        canvas.paste(im, (margin + (width - im.width) // 2, y))
        y += im.height + gap
    canvas.save(FIG / "fig_fields_plate.png", dpi=(220, 220))


def fig_curvature():
    """Final-only curvature panels with enlarged axes."""
    rows = readcsv(BASE / "01_curvature_validation" / "curvature_corrected_190.csv")
    fig, axes = plt.subplots(1, 2, figsize=(10.0, 4.2))
    sub = sorted((r for r in rows if float(r["Re"]) == 1000.0), key=lambda r: float(r["n"]))
    n = [float(r["n"]) for r in sub]
    axes[0].plot(n, [float(r["kappa_w_max"]) for r in sub], "o-", lw=1.8,
                 label=r"$\kappa_{w,\max}$")
    axes[0].plot(n, [float(r["kappa_w_rms"]) for r in sub], "s--", lw=1.6,
                 label=r"$\kappa_{w,\rm rms}$")
    axes[0].axhline(1.0, color="0.6", lw=1.0, ls=":")
    axes[0].set_xlabel(r"$n$", fontsize=12)
    axes[0].set_ylabel("window curvature", fontsize=12)
    axes[0].tick_params(labelsize=10)
    axes[0].legend(fontsize=10, frameon=False)
    axes[0].grid(alpha=0.3)

    for Re, marker in ((100.0, "o"), (500.0, "s"), (1000.0, "^")):
        s = sorted((r for r in rows if float(r["Re"]) == Re), key=lambda r: float(r["n"]))
        axes[1].plot([float(r["kappa_w_rms"]) for r in s],
                     [float(r["D_over_A_mask"]) for r in s], marker + "-", ms=4,
                     label=r"$Re=%d$" % Re)
    axes[1].set_xlabel(r"$\kappa_{w,\rm rms}$", fontsize=12)
    axes[1].set_ylabel(r"$D/A_{\rm mask}$", fontsize=12)
    axes[1].tick_params(labelsize=10)
    axes[1].legend(fontsize=10, frameon=False)
    axes[1].grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "fig_curvature.png", dpi=220)
    plt.close(fig)


def fig_nearwall_large_axes():
    """Enlarged-axis near-wall diagnostic used in the supplement."""
    rows = readcsv(BASE / "01_curvature_validation" / "curvature_corrected_190.csv")
    res = (100.0, 500.0, 1000.0)
    fig, axes = plt.subplots(1, 3, figsize=(12.0, 4.2))
    ref = sorted((r for r in rows if float(r["Re"]) == res[0]), key=lambda r: float(r["n"]))
    axes[0].plot([float(r["n"]) for r in ref], [float(r["kappa_w_max"]) for r in ref],
                 "o-", lw=1.8, label=r"$\kappa_{w,\max}$")
    axes[0].plot([float(r["n"]) for r in ref], [float(r["kappa_w_rms"]) for r in ref],
                 "s--", lw=1.6, label=r"$\kappa_{w,\rm rms}$")
    axes[0].axhline(1.0, color="0.6", lw=1.0, ls=":")
    axes[0].set_title("Window curvature", fontsize=12)
    axes[0].set_xlabel(r"$n$", fontsize=12)
    axes[0].set_ylabel("curvature", fontsize=12)
    axes[0].legend(fontsize=9, frameon=False)
    axes[0].grid(alpha=0.3)

    for Re in res:
        s = sorted((r for r in rows if float(r["Re"]) == Re), key=lambda r: float(r["n"]))
        axes[1].plot([float(r["n"]) for r in s], [float(r["f_band_0.025"]) for r in s],
                     "o-", ms=4, label=r"$Re=%d$" % Re)
        axes[1].plot([float(r["n"]) for r in s], [float(r["f_band_0.05"]) for r in s],
                     "s--", ms=3.5, alpha=0.7)
    axes[1].set_title("Wall-band dissipation share", fontsize=12)
    axes[1].set_xlabel(r"$n$", fontsize=12)
    axes[1].set_ylabel(r"$D_\delta/D$", fontsize=12)
    axes[1].legend(fontsize=9, frameon=False)
    axes[1].grid(alpha=0.3)

    for Re in res:
        s = [r for r in rows if float(r["Re"]) == Re]
        axes[2].plot([float(r["f_band_0.025"]) for r in s],
                     [float(r["D_over_A_mask"]) for r in s], "o", ms=5,
                     label=r"$Re=%d$" % Re)
    axes[2].set_yscale("log")
    axes[2].set_title("Loss density versus localization", fontsize=12)
    axes[2].set_xlabel(r"$D_{0.025L_c}/D$", fontsize=12)
    axes[2].set_ylabel(r"$D/A_{\rm mask}$", fontsize=12)
    axes[2].legend(fontsize=9, frameon=False)
    axes[2].grid(alpha=0.3, which="both")

    for ax in axes:
        ax.tick_params(labelsize=10)
    fig.tight_layout()
    fig.savefig(FIG / "fig_nearwall_large_axes.png", dpi=220)
    plt.close(fig)


def fig_minima():
    rows = readcsv(BASE / "05_minima_qualification" / "fit_diagnostics.csv")
    selected = []
    for r in rows:
        if r["group"] != "N128_union" or r["quantity"] != "D_over_A_mask":
            continue
        if not r["estimator"].startswith("OLS quadratic"):
            continue
        selected.append(r)
    if not selected:
        return
    fig, ax = plt.subplots(figsize=(6.6, 3.6))
    for est, marker in (("OLS quadratic, 3 points", "o"),
                        ("OLS quadratic, 5 points", "s")):
        s = [r for r in selected if r["estimator"] == est]
        s.sort(key=lambda r: float(r["Re"]))
        ax.plot([float(r["Re"]) for r in s], [float(r["n_star"]) for r in s],
                marker + "-", ms=4, label=est.replace("OLS quadratic, ", ""))
    ax.set_xlabel(r"$Re$"); ax.set_ylabel(r"fitted $n^*_{D/A}$")
    ax.grid(alpha=0.3); ax.legend(fontsize=8)
    ax.set_title("Fit-window sensitivity (same archived fields)")
    fig.tight_layout()
    fig.savefig(FIG / "fig_minima_windows.png", dpi=200)
    plt.close(fig)


def fig_fem():
    p = BASE / "03_FEM_dissipation_validation" / "fem_dissipation.csv"
    if not p.exists():
        return
    rows = readcsv(p)
    if not rows:
        return
    fig, axes = plt.subplots(1, 2, figsize=(9.4, 3.5))
    for Re in (100.0, 400.0, 1000.0):
        s = [r for r in rows if float(r["Re"]) == Re]
        s.sort(key=lambda r: (float(r["n"]), int(r["nrefs"])))
        for n in (1.25, 2.0, 4.0, 8.0):
            t = [r for r in s if abs(float(r["n"]) - n) < 1e-9]
            axes[0].plot([int(r["nrefs"]) for r in t],
                         [float(r["D_FEM_exact"]) for r in t], "o-", ms=3,
                         label=r"$n=%g$" % n if Re == 1000.0 else None)
    axes[0].set_xlabel("mesh refinement level"); axes[0].set_ylabel(r"$D_{\rm FEM}=2\nu\int S:S$")
    axes[0].grid(alpha=0.3); axes[0].legend(fontsize=7)
    axes[0].set_title("Exact integrated dissipation, P2/P1")

    q = BASE / "03_FEM_dissipation_validation" / "fem_gradient_reconstruction.csv"
    if q.exists():
        rr = [r for r in readcsv(q) if int(r["n_points"]) >= 1000]
        for Re in (100.0, 400.0, 1000.0):
            s = [r for r in rr if float(r["Re"]) == Re]
            s.sort(key=lambda r: float(r["n"]))
            axes[1].plot([float(r["n"]) for r in s],
                         [100 * float(r["eps_grad"]) for r in s], "o-", ms=4,
                         label=r"$Re=%d$, grad" % Re)
            axes[1].plot([float(r["n"]) for r in s],
                         [100 * float(r["rel_D_lattice_error"]) for r in s], "s--",
                         ms=3, label=r"$Re=%d$, $D$" % Re)
    axes[1].set_xlabel(r"$n$")
    axes[1].set_ylabel("relative error [%]")
    axes[1].grid(alpha=0.3); axes[1].legend(fontsize=6)
    axes[1].set_title("FD reconstruction from sampled FEM field")
    fig.tight_layout()
    fig.savefig(FIG / "fig_fem_validation.png", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    fig_budget()
    fig_junction()
    fig_dissipation()
    fig_fields_plate()
    fig_curvature()
    fig_nearwall_large_axes()
    fig_minima()
    fig_fem()
    print("figures ->", FIG)
