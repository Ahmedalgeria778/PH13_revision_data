# -*- coding: utf-8 -*-
"""Figures for the restructured physics-only manuscript.

All panels are generated from CSVs produced by the executed correction scripts
in ../01..05.  No numeric value is typed by hand.
"""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

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


def fig_curvature():
    new = readcsv(BASE / "01_curvature_validation" / "curvature_corrected_190.csv")
    old = readcsv(BASE / "01_curvature_validation" / "curvature_before_after.csv")
    fig, axes = plt.subplots(1, 2, figsize=(9.4, 3.5))
    sub = [r for r in new if float(r["Re"]) == 1000.0]
    sub.sort(key=lambda r: float(r["n"]))
    n = [float(r["n"]) for r in sub]
    axes[0].plot(n, [float(r["kappa_w_max"]) for r in sub], "o-",
                 label=r"$\kappa_{w,\max}$ (corrected)")
    axes[0].plot(n, [float(r["kappa_w_rms"]) for r in sub], "s--",
                 label=r"$\kappa_{w,\rm rms}$ (corrected)")
    o = [r for r in old if float(r["Re"]) == 1000.0]
    o.sort(key=lambda r: float(r["n"]))
    axes[0].plot([float(r["n"]) for r in o], [float(r["old_kappa_w_max"]) for r in o],
                 "x:", color="0.5", label=r"$\kappa_{w,\max}$ (old, defective)")
    axes[0].set_xlabel(r"$n$"); axes[0].set_ylabel("window curvature")
    axes[0].legend(fontsize=7); axes[0].grid(alpha=0.3)
    axes[0].set_title("Circle test: corrected $n=2$ gives $\\kappa=1$")

    sub2 = [r for r in new if float(r["Re"]) in (100.0, 1000.0)]
    for Re in (100.0, 1000.0):
        s = [r for r in sub2 if float(r["Re"]) == Re]
        s.sort(key=lambda r: float(r["n"]))
        axes[1].plot([float(r["n"]) for r in s],
                     [float(r["kappa_D_weighted"]) for r in s], "o-",
                     label=r"$Re=%d$" % Re)
    axes[1].set_xlabel(r"$n$")
    axes[1].set_ylabel(r"dissipation-weighted $\langle\kappa_w\rangle_D$")
    axes[1].legend(fontsize=8); axes[1].grid(alpha=0.3)
    axes[1].set_title("Corrected curvature reverses the former $n$-trend")
    fig.tight_layout()
    fig.savefig(FIG / "fig_curvature_corrected.png", dpi=200)
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
    fig_curvature()
    fig_minima()
    fig_fem()
    print("figures ->", FIG)
