# -*- coding: utf-8 -*-
"""Figures for the final physics-only manuscript and its supplement.

All quantitative panels are generated from the archived CSVs and the saved
N=128 fields.  No numeric value is typed by hand.  The readability edits in
this version use distinct markers and line styles for every case, so that the
figures remain interpretable after black-and-white printing; the plotted data
and the plotted samples are unchanged.

Set PH13_FIG_DIR to write into a different figs_new directory; --only limits
the run to named output files.
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import os
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

OUT = Path(__file__).resolve().parent
FIG = Path(os.environ.get("PH13_FIG_DIR", str(OUT / "figs_new")))
FIG.mkdir(parents=True, exist_ok=True)
ROOT = Path(r"C:\Users\user\Documents\Default Project\GIRVD (revised)")
DATA = ROOT / "corrections for reviewer" / "PH13_revision_data" / "data"
FIELD_DATA = ROOT / "05_dataset" / "data"
_PHYSICS = None

# Distinct marker/line-style pairs so that colour is never the only discriminator
# when the figures are printed in black and white.
RE_STYLES = {
    100.0: ("o", "-"),
    300.0: ("s", "--"),
    500.0: ("^", "-."),
    1000.0: ("D", ":"),
}


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
    rows = readcsv(DATA / "core_wall" / "core_wall_budget.csv")
    fig, axes = plt.subplots(1, 3, figsize=(13.2, 4.4), sharex=True, sharey=True)
    for i, (ax, Re) in enumerate(zip(axes, (300.0, 500.0, 1000.0))):
        sub = [r for r in rows if float(r["Re"]) == Re and int(r["N"]) == 256
               and abs(float(r["delta_over_Lc"]) - 0.05) < 1e-12]
        sub.sort(key=lambda r: float(r["n"]))
        n = [float(r["n"]) for r in sub]
        ax.plot(n, [float(r["Dmask_over_A"]) for r in sub], "k-o", lw=1.8,
                ms=4, label=r"$D/A_{\rm mask}$")
        ax.plot(n, [float(r["Dwall_over_A"]) for r in sub], "ks--", lw=1.6,
                ms=4, label=r"$D_{\rm wall}/A_{\rm mask}$")
        ax.plot(n, [float(r["Dcore_over_A"]) for r in sub], "k^:", lw=1.8,
                ms=5, label=r"$D_{\rm core}/A_{\rm mask}$")
        ax.set_title("(%s) $Re=%d,\\ N=256$" % ("abc"[i], Re), fontsize=14)
        ax.set_xlabel(r"$n$", fontsize=14)
        ax.tick_params(labelsize=12, pad=5)
        ax.grid(alpha=0.3)
    axes[0].set_ylabel(r"dissipation per unit $A_{\rm mask}$", fontsize=14)
    axes[0].legend(fontsize=11, loc="best", frameon=False)
    fig.suptitle("Additive core/wall budget: the rise beyond the low-loss band is core-driven",
                 fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    fig.savefig(FIG / "fig_core_wall_budget.png", dpi=200)
    plt.close(fig)


def fig_junction():
    rows = readcsv(DATA / "junction" / "junction_budget.csv")
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.4), sharey=True)
    n_styles = {
        1.25: ("o", "-"),
        2.0: ("s", "--"),
        4.0: ("^", "-."),
        8.0: ("D", ":"),
    }
    for i, (ax, Re) in enumerate(zip(axes, (100.0, 1000.0))):
        for n in (1.25, 2.0, 4.0, 8.0):
            sub = [r for r in rows if float(r["Re"]) == Re and abs(float(r["n"]) - n) < 1e-9]
            sub.sort(key=lambda r: float(r["r_over_Lc"]))
            marker, ls = n_styles[n]
            ax.plot([float(r["r_over_Lc"]) for r in sub],
                    [100 * float(r["f_junction"]) for r in sub],
                    marker=marker, linestyle=ls, color="k", lw=1.5, ms=4.5,
                    label=r"$n=%g$" % n)
        ax.set_title("(%s) $Re=%d$" % ("ab"[i], Re), fontsize=13)
        ax.set_xlabel(r"excision radius $r/L_c$", fontsize=13)
        ax.tick_params(labelsize=11, pad=5)
        ax.grid(alpha=0.3)
    axes[0].set_ylabel(r"$100\,D_{\rm junction}/D_{\rm mask}$  [\%]", fontsize=13)
    axes[0].legend(fontsize=10, loc="best", frameon=False)
    fig.suptitle("Dissipation inside the two tangential-lid junction disks", fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, 0.91))
    fig.savefig(FIG / "fig_junction_share.png", dpi=200)
    plt.close(fig)


def read_dissipation():
    """Same archived 190-case observable table used by the original figures."""
    rows = readcsv(ROOT / "06_physics" / "results_190" / "physics_observables.csv")
    res = sorted({float(r["Re"]) for r in rows})
    ns = sorted({float(r["n"]) for r in rows})
    values = np.full((len(res), len(ns)), np.nan)
    n_index = {n: j for j, n in enumerate(ns)}
    r_index = {r: i for i, r in enumerate(res)}
    for r in rows:
        values[r_index[float(r["Re"])], n_index[float(r["n"])]] = (
            float(r["dissipation"]) / float(r["area_mask"]))
    return rows, res, ns, values


def fig_curve_dissipation():
    """Figure 2a: unchanged curve panel."""
    rows, res, ns, values = read_dissipation()
    highlighted = (100.0, 300.0, 500.0, 1000.0)
    colors = {100.0: "#2b6cb0", 300.0: "#2f855a", 500.0: "#c05621", 1000.0: "#6b46c1"}

    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    for Re in res:
        sub = sorted((r for r in rows if abs(float(r["Re"]) - Re) < 1e-9),
                     key=lambda r: float(r["n"]))
        n = [float(r["n"]) for r in sub]
        d = [float(r["dissipation"]) for r in sub]
        if Re in highlighted:
            marker, ls = RE_STYLES[Re]
            ax.plot(n, d, marker=marker, linestyle=ls, ms=4.5, lw=1.8,
                    color=colors[Re], label=r"$Re=%d$" % Re)
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


def fig_map_dissipation():
    """Normalized D/A curves: every Re is plotted, four are highlighted."""
    rows, res, ns, values = read_dissipation()
    highlighted = (100.0, 300.0, 500.0, 1000.0)
    colors = {100.0: "#2b6cb0", 300.0: "#2f855a", 500.0: "#c05621", 1000.0: "#6b46c1"}

    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    for Re in res:
        sub = sorted((r for r in rows if float(r["Re"]) == Re),
                     key=lambda r: float(r["n"]))
        n = np.array([float(r["n"]) for r in sub])
        da = np.array([float(r["dissipation"]) / float(r["area_mask"]) for r in sub])
        normalized = da / np.nanmin(da)
        if Re in highlighted:
            marker, ls = RE_STYLES[Re]
            ax.plot(n, normalized, marker=marker, linestyle=ls, ms=5, lw=1.8,
                    color=colors[Re], label=r"$Re=%d$" % Re)
        else:
            ax.plot(n, normalized, "-", lw=0.8, color="0.78", zorder=0)
    ax.axhline(1.0, color="0.45", lw=1.0, ls=":")
    ax.set_xlabel("superellipse exponent $n$", fontsize=14, labelpad=8)
    ax.set_ylabel(r"$(D/A_{\rm mask})/\min(D/A_{\rm mask})$", fontsize=14, labelpad=8)
    ax.tick_params(axis="both", labelsize=12, pad=6)
    xticks = [n for n in ns if n in (1.25, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0)]
    ax.set_xticks(xticks)
    ax.set_xticklabels(["%g" % n for n in xticks], rotation=30, ha="right")
    ax.set_ylim(0.95, None)
    ax.grid(alpha=0.25)
    ax.legend(fontsize=10, frameon=False, ncol=2, loc="best")
    fig.tight_layout()
    fig.savefig(FIG / "map_dissipation.png", dpi=220)
    plt.close(fig)


def fig_dissipation(which="both"):
    """Backward-compatible entry point for the two Figure 2 panels."""
    if which in ("both", "curve"):
        fig_curve_dissipation()
    if which in ("both", "map"):
        fig_map_dissipation()


def _physics_module():
    """Frozen analysis helpers used to rebuild the field panels from the npz."""
    global _PHYSICS
    if _PHYSICS is None:
        path = FIELD_DATA / "analyse_physique_mapping.py"
        spec = importlib.util.spec_from_file_location("ph13_analyse_physique_mapping", path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        _PHYSICS = mod
    return _PHYSICS


def fig_fields_plate():
    """Figure 3: replot the four archived N=128, Re=1000 fields in English.

    The panels are recomputed from the same saved fields with the frozen
    analysis helpers; no native title band (French or otherwise) is reused.
    """
    phys = _physics_module()
    cases = [("n1p25", r"$n=1.25$"), ("n2p0", r"$n=2$"),
             ("n4p0", r"$n=4$"), ("n8p0", r"$n=8$")]
    column_titles = [r"$|U|/U_{\rm lid}$", r"Vorticity $\omega$",
                     r"Streamfunction $\psi$ (diagnostic)"]
    fig, axes = plt.subplots(4, 3, figsize=(23.0, 24.0), constrained_layout=True)

    for r, (stem, nlabel) in enumerate(cases):
        path = FIELD_DATA / ("se_%s_Re1000_N128.npz" % stem)
        with np.load(path, allow_pickle=False) as z:
            ux = np.asarray(z["ux"], dtype=float)
            uy = np.asarray(z["uy"], dtype=float)
            fluid = np.asarray(z["fluid"], dtype=bool)
            X = np.asarray(z["X"], dtype=float)
            Y = np.asarray(z["Y"], dtype=float)
            U_lid = float(np.asarray(z["U_lid"]).item())
        dx = float(phys._median_step(X, axis=1))
        dy = float(phys._median_step(Y, axis=0))
        valid, _ = phys._build_gradient_masks(fluid)
        der = phys._derivatives(ux, uy, dx, dy, valid)
        omega = der["uy_x"] - der["ux_y"]
        omega[~valid] = np.nan
        psi = phys.solve_streamfunction(omega, fluid, dx, dy)
        fields = [np.hypot(ux, uy) / U_lid, omega, psi]

        for c, (field, title) in enumerate(zip(fields, column_titles)):
            ax = axes[r, c]
            masked = phys._mask_field(field, fluid)
            finite = field[fluid & np.isfinite(field)]
            vmin = float(np.min(finite)) if finite.size else -1.0
            vmax = float(np.max(finite)) if finite.size else 1.0
            if c > 0 and vmin < 0.0 and vmax > 0.0:
                vmax_abs = max(abs(vmin), abs(vmax))
                levels = np.linspace(-vmax_abs, vmax_abs, 41)
                norm = matplotlib.colors.TwoSlopeNorm(
                    vcenter=0.0, vmin=-vmax_abs, vmax=vmax_abs)
                contour = ax.contourf(X, Y, masked, levels=levels, norm=norm)
            else:
                contour = ax.contourf(X, Y, masked, levels=35)
            ax.contour(X, Y, fluid.astype(float), levels=[0.5],
                       linewidths=0.8, colors="k")
            ax.set_aspect("equal")
            ax.set_xlabel("x", fontsize=14)
            ax.set_ylabel((nlabel + "\ny") if c == 0 else "y", fontsize=14)
            ax.tick_params(labelsize=12, pad=4)
            if r == 0:
                ax.set_title(title, fontsize=17)
            cb = fig.colorbar(contour, ax=ax, fraction=0.046, pad=0.04)
            cb.set_label(title, fontsize=13)
            cb.ax.tick_params(labelsize=10)
    fig.savefig(FIG / "fig_fields_plate.png", dpi=200)
    plt.close(fig)


def fig_curvature():
    """Final-only curvature panels with enlarged axes."""
    rows = readcsv(DATA / "curvature" / "curvature_corrected_190.csv")
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

    for Re, (marker, ls) in ((100.0, RE_STYLES[100.0]),
                             (500.0, RE_STYLES[500.0]),
                             (1000.0, RE_STYLES[1000.0])):
        s = sorted((r for r in rows if float(r["Re"]) == Re), key=lambda r: float(r["n"]))
        axes[1].plot([float(r["kappa_w_rms"]) for r in s],
                     [float(r["D_over_A_mask"]) for r in s],
                     marker=marker, linestyle=ls, ms=4.5, lw=1.6,
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
    rows = readcsv(DATA / "curvature" / "curvature_corrected_190.csv")
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

    re_markers = {100.0: "o", 500.0: "s", 1000.0: "^"}
    for Re in res:
        s = sorted((r for r in rows if float(r["Re"]) == Re), key=lambda r: float(r["n"]))
        axes[1].plot([float(r["n"]) for r in s], [float(r["f_band_0.025"]) for r in s],
                     marker=re_markers[Re], linestyle="-", ms=4.5, lw=1.6,
                     label=r"$Re=%d$, $\delta=0.025L_c$" % Re)
        axes[1].plot([float(r["n"]) for r in s], [float(r["f_band_0.05"]) for r in s],
                     marker=re_markers[Re], linestyle="--", ms=3.5, lw=1.4,
                     alpha=0.85,
                     label=r"$Re=%d$, $\delta=0.05L_c$" % Re)
    axes[1].set_title("Wall-band dissipation share", fontsize=12)
    axes[1].set_xlabel(r"$n$", fontsize=12)
    axes[1].set_ylabel(r"$D_\delta/D$", fontsize=12)
    axes[1].legend(fontsize=7.5, frameon=False, ncol=2)
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
    rows = readcsv(DATA / "minima" / "fit_diagnostics.csv")
    selected = []
    for r in rows:
        if r["group"] != "N128_union" or r["quantity"] != "D_over_A_mask":
            continue
        if not r["estimator"].startswith("OLS quadratic"):
            continue
        selected.append(r)
    if not selected:
        return
    fig, ax = plt.subplots(figsize=(8.2, 4.4))
    for est, marker, ls in (("OLS quadratic, 3 points", "o", "-"),
                            ("OLS quadratic, 5 points", "s", "--")):
        s = [r for r in selected if r["estimator"] == est]
        s.sort(key=lambda r: float(r["Re"]))
        ax.plot([float(r["Re"]) for r in s], [float(r["n_star"]) for r in s],
                marker=marker, linestyle=ls, color="k", ms=5, lw=1.6,
                label=est.replace("OLS quadratic, ", ""))
    ax.set_xlabel(r"$Re$", fontsize=14)
    ax.set_ylabel(r"fitted $n^*_{D/A}$", fontsize=14)
    ax.tick_params(labelsize=12, pad=5)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=11, frameon=False)
    ax.set_title("Fit-window sensitivity (same archived fields)", fontsize=13)
    fig.tight_layout()
    fig.savefig(FIG / "fig_minima_windows.png", dpi=200)
    plt.close(fig)


def fig_fem():
    p = DATA / "fem" / "fem_dissipation.csv"
    if not p.exists():
        return
    rows = readcsv(p)
    if not rows:
        return
    fig, axes = plt.subplots(1, 2, figsize=(12.0, 4.6))
    n_markers = {1.25: "o", 2.0: "s", 4.0: "^", 8.0: "D"}
    re_styles = {100.0: "-", 400.0: "--", 1000.0: "-."}
    for Re in (100.0, 400.0, 1000.0):
        s = [r for r in rows if float(r["Re"]) == Re]
        s.sort(key=lambda r: (float(r["n"]), int(r["nrefs"])))
        for n in (1.25, 2.0, 4.0, 8.0):
            t = [r for r in s if abs(float(r["n"]) - n) < 1e-9]
            axes[0].plot([int(r["nrefs"]) for r in t],
                         [float(r["D_FEM_exact"]) for r in t],
                         marker=n_markers[n], linestyle=re_styles[Re],
                         color="0.25", ms=4, lw=1.4)
    n_handles = [Line2D([], [], color="0.25", marker=n_markers[n],
                        linestyle="None", ms=5, label=r"$n=%g$" % n)
                 for n in (1.25, 2.0, 4.0, 8.0)]
    re_handles = [Line2D([], [], color="0.25", linestyle=re_styles[Re],
                         lw=1.6, label=r"$Re=%d$" % Re)
                  for Re in (100.0, 400.0, 1000.0)]
    axes[0].legend(handles=n_handles + re_handles, fontsize=10, frameon=False,
                   ncol=2, handlelength=2.4)
    axes[0].set_xlabel("mesh refinement level", fontsize=14)
    axes[0].set_ylabel(r"$D_{\rm FEM}=2\nu\int S:S$", fontsize=14)
    axes[0].tick_params(labelsize=12, pad=5)
    axes[0].grid(alpha=0.3)
    axes[0].set_title("(a) Exact integrated dissipation, P2/P1", fontsize=14)

    q = DATA / "fem" / "fem_gradient_reconstruction.csv"
    if q.exists():
        rr = [r for r in readcsv(q) if int(r["n_points"]) >= 1000]
        re_markers = {100.0: "o", 400.0: "s", 1000.0: "^"}
        for Re in (100.0, 400.0, 1000.0):
            s = [r for r in rr if float(r["Re"]) == Re]
            s.sort(key=lambda r: float(r["n"]))
            axes[1].plot([float(r["n"]) for r in s],
                         [100 * float(r["eps_grad"]) for r in s],
                         marker=re_markers[Re], linestyle="-", ms=4.5, lw=1.5,
                         label=r"$Re=%d$, grad" % Re)
            axes[1].plot([float(r["n"]) for r in s],
                         [100 * float(r["rel_D_lattice_error"]) for r in s],
                         marker=re_markers[Re], linestyle="--", ms=3.5, lw=1.3,
                         label=r"$Re=%d$, $D$" % Re)
    axes[1].set_xlabel(r"$n$", fontsize=14)
    axes[1].set_ylabel("relative error [%]", fontsize=14)
    axes[1].tick_params(labelsize=12, pad=5)
    axes[1].grid(alpha=0.3)
    axes[1].legend(fontsize=9.5, frameon=False, ncol=2)
    axes[1].set_title("(b) FD reconstruction from sampled FEM field", fontsize=14)
    fig.tight_layout()
    fig.savefig(FIG / "fig_fem_validation.png", dpi=200)
    plt.close(fig)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--only", nargs="*", default=None,
                    help="regenerate only the listed output file names")
    args = ap.parse_args(argv)
    jobs = {
        "fig_core_wall_budget.png": fig_budget,
        "fig_junction_share.png": fig_junction,
        "curve_dissipation_vs_n.png": fig_curve_dissipation,
        "map_dissipation.png": fig_map_dissipation,
        "fig_fields_plate.png": fig_fields_plate,
        "fig_curvature.png": fig_curvature,
        "fig_nearwall_large_axes.png": fig_nearwall_large_axes,
        "fig_minima_windows.png": fig_minima,
        "fig_fem_validation.png": fig_fem,
    }
    selected = args.only
    for name, fn in jobs.items():
        if selected is None or name in selected:
            fn()
    print("figures ->", FIG)


if __name__ == "__main__":
    main()
