# -*- coding: utf-8 -*-
"""Campagne A -- dissipation on FIXED PHYSICAL supports, from archived fields.

No new LBM run is performed.  Every archived macroscopic field is recomputed on
a support defined in physical coordinates:

    M_{r0}      = gradient-valid fluid nodes outside the two junction disks,
    M_{delta,r0}= M_{r0} cap {dist(x, Gamma_n) > delta},

where dist is the distance to the exact superellipse boundary sampled by
``Superellipse.boundary_points`` and queried with a KD-tree in physical space.
The production-scaled dissipation is

    D = 2 * sum_{M} (S_lbm:S_lbm / Re) * h_N^2,     h_N = 2/(N-1),

the same convention as ``dcore_test.py`` and ``analyse_diffusive_scaling.py``.
Schemes (production, diffusive, lid-projected, snapshot, smoke, checkpoint) are
tagged and never silently mixed; paired geometry differences use only primary
production fields (and the separate diffusive ladder is reported on its own).

Outputs, all inside PH13_revision_data:
    data/campaign_a/campaign_a_dissipation.csv
    data/campaign_a/campaign_a_paired_differences.csv
    data/campaign_a/campaign_a_minimum_stability.csv
    data/campaign_a/campaign_a_annuli.csv
    data/campaign_a/README_campaign_A.md
    figures/campaign_a/fig_campaign_a_delta_r0_sensitivity.png
    figures/campaign_a/fig_campaign_a_paired_differences.png
    figures/campaign_a/fig_campaign_a_minimum_stability.png
    figures/campaign_a/fig_campaign_a_junction_annuli.png
    figures/campaign_a/alt_text_campaign_A.txt
"""
from __future__ import annotations

import csv
import math
import sys
import time
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import cKDTree

HERE = Path(__file__).resolve().parent


def _find_repo_root(start: Path) -> Path:
    for cand in (start,) + tuple(start.parents):
        if (cand / "05_dataset").is_dir():
            return cand
    return start.parent.parent


ROOT = _find_repo_root(HERE)
PKG = HERE.parent.parent
DATA_ROOT = ROOT / "05_dataset"
if str(ROOT / "01_geometry") not in sys.path:
    sys.path.insert(0, str(ROOT / "01_geometry"))
from superellipse import Superellipse  # noqa: E402

OUT_DATA = PKG / "data" / "campaign_a"
OUT_FIG = PKG / "figures" / "campaign_a"
OUT_REPORT = PKG / "reports"

DELTA_FRACTIONS = (0.025, 0.05, 0.10)
R0_VALUES = (0.0, 0.03125, 0.0625, 0.125, 0.25)
JUNCTIONS = ((1.0, 0.0), (-1.0, 0.0))
L_C_DEFAULT = 2.0
N_BOUNDARY = 120_000
ANNULUS_RADII = (0.0078125, 0.015625, 0.03125, 0.0625, 0.125, 0.25)
FOCUS_PAIRS = ((2.0, 4.0), (3.0, 4.0), (4.0, 5.0), (4.0, 8.0),
               (2.0, 8.0), (1.25, 8.0))

PROD_PRIORITY = {
    "data": 0, "data_all190": 1, "data_corner": 2, "data_convHR": 3,
    "data_conv256": 4, "data_conv": 5, "data_convHR_extB": 6,
    "data_re_ext": 7, "data_re_ext_b": 8, "data_refine": 9,
    "data_refine_seed": 10, "data_all100": 11, "data_all120": 12,
}
SCHEME_PRIORITY = {"production": 0, "diffusive": 1, "projected": 2,
                   "snapshot": 3, "smoke": 4}


# ---------------------------------------------------------------------------
# Inventory and scheme tagging
# ---------------------------------------------------------------------------
def classify(path: Path) -> tuple[str, str, int]:
    rel = path.relative_to(ROOT).as_posix()
    low = path.name.lower()
    if "_ckpt" in low:
        return "checkpoint", rel, 99
    if "_smoke" in rel:
        return "smoke", rel, 4
    if "data_diffusive" in rel:
        return "diffusive", rel, 1
    if "lid_projected" in rel:
        return "projected", rel, 2
    if "snapshot" in rel:
        return "snapshot", rel, 3
    if "diagnostics" in rel:
        return "diagnostic", rel, 5
    scheme = "production"
    parts = rel.split("/")
    folder = parts[1] if len(parts) > 1 else ""
    return scheme, rel, PROD_PRIORITY.get(folder, 20)


def _scalar(z, key, default=None):
    if key not in z.files:
        return default
    try:
        return z[key].item()
    except Exception:
        return default


def scan_fields() -> list[dict]:
    """Lightweight metadata scan; final fields only (no checkpoints)."""
    found = []
    for path in sorted(DATA_ROOT.rglob("*.npz")):
        scheme, rel, prio = classify(path)
        if scheme in ("checkpoint", "diagnostic"):
            continue
        with np.load(path, allow_pickle=False) as z:
            required = ("ux", "uy", "fluid", "X", "Y", "N", "Re", "n")
            if any(k not in z.files for k in required):
                continue
            n, re, N = _scalar(z, "n"), _scalar(z, "Re"), _scalar(z, "N")
            if n is None or re is None or N is None:
                continue
            rec = {
                "path": path, "rel": rel, "scheme": scheme,
                "priority": prio, "n": float(n), "Re": float(re), "N": int(N),
                "U_lid": _scalar(z, "U_lid", float("nan")),
                "nu_lbm": _scalar(z, "nu_lbm", float("nan")),
                "L_c": float(_scalar(z, "L_c", L_C_DEFAULT)),
                "a": float(_scalar(z, "a", 1.0)),
                "b": float(_scalar(z, "b", 1.0)),
            }
        found.append(rec)

    # One primary file per (scheme, n, Re, N).  Production uses the frozen
    # reference priority table; other schemes are kept strictly separate.
    groups = defaultdict(list)
    for rec in found:
        groups[(rec["scheme"], round(rec["n"], 9), round(rec["Re"], 9),
                rec["N"])].append(rec)
    for members in groups.values():
        members.sort(key=lambda r: (r["priority"], r["path"].name))
        for i, rec in enumerate(members):
            rec["primary"] = (i == 0)
            rec["duplicates_in_group"] = len(members)
    for rec in found:
        rec["analysis_eligible"] = bool(
            rec["primary"] and rec["scheme"] in ("production", "diffusive"))
    return found


# ---------------------------------------------------------------------------
# Geometry / numerics
# ---------------------------------------------------------------------------
@lru_cache(maxsize=32)
def boundary_tree(n: float, a: float, b: float) -> tuple[cKDTree, np.ndarray]:
    pts = Superellipse(a=a, b=b, n=n).boundary_points(
        num=N_BOUNDARY, arc_uniform=True)
    return cKDTree(pts), pts


def gradient_valid_mask(fluid: np.ndarray) -> np.ndarray:
    v = np.zeros_like(fluid, dtype=bool)
    v[1:-1, 1:-1] = (fluid[1:-1, 1:-1] & fluid[:-2, 1:-1] & fluid[2:, 1:-1]
                     & fluid[1:-1, :-2] & fluid[1:-1, 2:])
    return v


def read_field(rec: dict) -> dict:
    with np.load(rec["path"], allow_pickle=False) as z:
        out = dict(rec)
        out["ux"] = np.asarray(z["ux"], dtype=float)
        out["uy"] = np.asarray(z["uy"], dtype=float)
        out["fluid"] = np.asarray(z["fluid"], dtype=bool)
        out["X"] = np.asarray(z["X"], dtype=float)
        out["Y"] = np.asarray(z["Y"], dtype=float)
        out["tau_lbm"] = float(_scalar(z, "tau_lbm",
                                      0.5 + 3.0 * rec["nu_lbm"]))
    return out


def strain_density(field: dict) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    ux, uy = field["ux"], field["uy"]
    X = field["X"]
    N = field["N"]
    h = 2.0 / (N - 1)
    if abs(abs(float(X[0, 1] - X[0, 0])) - h) > 1e-10:
        raise ValueError(f"unexpected grid spacing in {field['rel']}")
    valid = gradient_valid_mask(field["fluid"])
    gx = np.full(ux.shape, np.nan)
    gy = np.full(ux.shape, np.nan)
    vx = np.full(ux.shape, np.nan)
    vy = np.full(ux.shape, np.nan)
    gx[1:-1, 1:-1] = (ux[1:-1, 2:] - ux[1:-1, :-2]) / (2.0 * h)
    vx[1:-1, 1:-1] = (uy[1:-1, 2:] - uy[1:-1, :-2]) / (2.0 * h)
    gy[1:-1, 1:-1] = (ux[2:, 1:-1] - ux[:-2, 1:-1]) / (2.0 * h)
    vy[1:-1, 1:-1] = (uy[2:, 1:-1] - uy[:-2, 1:-1]) / (2.0 * h)
    sss = (2.0 * gx**2 + 2.0 * vy**2 + (gy + vx) ** 2) / field["Re"]
    phi = np.where(valid, sss, 0.0)
    tree, _ = boundary_tree(round(field["n"], 9), field["a"], field["b"])
    pts = np.column_stack((X.ravel(), field["Y"].ravel()))
    dist = tree.query(pts, workers=-1)[0].reshape(X.shape)
    return phi, valid, dist, h


def outside_junction_disks(field: dict, r0: float) -> np.ndarray:
    keep = np.ones(field["X"].shape, dtype=bool)
    if r0 > 0.0:
        for xj, yj in JUNCTIONS:
            keep &= np.hypot(field["X"] - xj, field["Y"] - yj) > r0
    return keep


def analyse_field(field: dict) -> list[dict]:
    phi, valid, dist, h = strain_density(field)
    cell = h * h
    rows = []
    for r0 in R0_VALUES:
        base = valid & outside_junction_disks(field, r0)
        d_base = 2.0 * float(np.sum(phi[base])) * cell
        for frac in DELTA_FRACTIONS:
            delta = frac * field["L_c"]
            core = base & (dist > delta)
            wall = base & (dist <= delta)
            d_core = 2.0 * float(np.sum(phi[core])) * cell
            d_wall = 2.0 * float(np.sum(phi[wall])) * cell
            a_core = float(np.count_nonzero(core)) * cell
            a_wall = float(np.count_nonzero(wall)) * cell
            rows.append({
                "scheme": field["scheme"], "primary": int(field["primary"]),
                "analysis_eligible": int(field["analysis_eligible"]),
                "source": field["rel"], "case_name": field["path"].name,
                "n": field["n"], "Re": field["Re"], "N": field["N"],
                "h": h, "U_lid": field["U_lid"], "nu_lbm": field["nu_lbm"],
                "tau_lbm": field["tau_lbm"], "L_c": field["L_c"],
                "delta_fraction": frac, "delta": delta, "r0": r0,
                "n_core": int(np.count_nonzero(core)),
                "n_wall": int(np.count_nonzero(wall)),
                "A_core": a_core, "A_wall": a_wall,
                "D_base": d_base, "D_core": d_core, "D_wall": d_wall,
                "q_core": d_core / a_core if a_core > 0.0 else float("nan"),
                "additivity_residual": d_core + d_wall - d_base,
            })
    return rows


# ---------------------------------------------------------------------------
# Junction annuli (preliminary diagnostic for Campagne B)
# ---------------------------------------------------------------------------
def is_annulus_case(field: dict) -> bool:
    return bool(
        field["analysis_eligible"] and field["scheme"] == "production"
        and field["Re"] == 1000.0 and field["n"] in (2.0, 4.0, 8.0)
        and field["N"] in (128, 256, 384, 512))


def annulus_diagnostics(loaded_fields: list[dict]) -> list[dict]:
    """Compute annuli from already-loaded fields (arrays present)."""
    out = []
    for field in loaded_fields:
        if not is_annulus_case(field):
            continue
        phi, valid, _, h = strain_density(field)
        cell = h * h
        s_mag = np.sqrt(np.maximum(phi, 0.0) * field["Re"])
        for j, (xj, yj) in enumerate(JUNCTIONS):
            rj = np.hypot(field["X"] - xj, field["Y"] - yj)
            for r in ANNULUS_RADII:
                ann = valid & (rj >= r) & (rj < 2.0 * r)
                count = int(np.count_nonzero(ann))
                if count == 0:
                    continue
                d_ann = 2.0 * float(np.sum(phi[ann])) * cell
                vals = r * s_mag[ann]
                out.append({
                    "n": field["n"], "Re": field["Re"], "N": field["N"],
                    "junction": "right" if j == 0 else "left",
                    "r": r, "ln_r": math.log(r), "n_cells": count,
                    "D_annulus": d_ann,
                    "mean_r_S": float(np.mean(vals)),
                    "max_r_S": float(np.max(vals)),
                    "source": field["rel"],
                })
    return out


# ---------------------------------------------------------------------------
# Paired differences and minimum stability
# ---------------------------------------------------------------------------
def write_paired_differences(rows: list[dict], path: Path) -> list[dict]:
    grouped = defaultdict(dict)
    for r in rows:
        if not r["analysis_eligible"]:
            continue
        key = (r["scheme"], r["Re"], r["N"], r["delta_fraction"], r["r0"])
        grouped[key][round(r["n"], 9)] = r
    paired = []
    for key, by_n in grouped.items():
        scheme, re, N, frac, r0 = key
        ns = sorted(by_n)
        for kind, pairs in (("focus", FOCUS_PAIRS),
                            ("adjacent", list(zip(ns[:-1], ns[1:])))):
            for ni, nj in pairs:
                if ni not in by_n or nj not in by_n or ni == nj:
                    continue
                ri, rj = by_n[ni], by_n[nj]
                d = ri["D_core"] - rj["D_core"]
                paired.append({
                    "scheme": scheme, "Re": re, "N": N, "h": ri["h"],
                    "delta_fraction": frac, "delta": ri["delta"], "r0": r0,
                    "pair_kind": kind, "n_i": ni, "n_j": nj,
                    "D_i": ri["D_core"], "D_j": rj["D_core"],
                    "delta_D": d, "ratio": ri["D_core"] / rj["D_core"],
                    "sign": "+" if d > 0 else ("-" if d < 0 else "0"),
                    "source_i": ri["source"], "source_j": rj["source"],
                })
    paired.sort(key=lambda r: (r["scheme"], r["Re"], r["N"],
                               r["delta_fraction"], r["r0"], r["pair_kind"],
                               r["n_i"], r["n_j"]))
    fields = ["scheme", "Re", "N", "h", "delta_fraction", "delta", "r0",
              "pair_kind", "n_i", "n_j", "D_i", "D_j", "delta_D", "ratio",
              "sign", "source_i", "source_j"]
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for r in paired:
            w.writerow({k: r[k] for k in fields})
    return paired


def write_minimum_stability(rows: list[dict], path: Path) -> list[dict]:
    by_case = defaultdict(dict)
    for r in rows:
        if not r["analysis_eligible"]:
            continue
        key = (r["scheme"], round(r["n"], 9), r["Re"],
               r["delta_fraction"], r["r0"])
        by_case[key][r["N"]] = r["D_core"]

    spreads = {}
    for key, by_N in by_case.items():
        Ns = sorted(by_N)
        vals = [by_N[N] for N in Ns]
        spreads[key] = max((abs(vals[i + 1] - vals[i])
                            for i in range(len(vals) - 1)), default=float("nan"))

    grouped = defaultdict(dict)
    for key, by_N in by_case.items():
        scheme, n, re, frac, r0 = key
        grouped[(scheme, re, frac, r0)][n] = by_N

    out = []
    for key, by_n in grouped.items():
        scheme, re, frac, r0 = key
        for N in sorted({N for by_N in by_n.values() for N in by_N}):
            available = [(n, by_N[N]) for n, by_N in by_n.items() if N in by_N]
            if len(available) < 2:
                continue
            available.sort(key=lambda t: t[1])
            (n1, d1), (n2, d2) = available[:2]
            k1 = (scheme, n1, re, frac, r0)
            k2 = (scheme, n2, re, frac, r0)
            s1, s2 = spreads[k1], spreads[k2]
            u = max(s1, s2)
            gap = d2 - d1
            out.append({
                "scheme": scheme, "Re": re, "N": N,
                "delta_fraction": frac, "r0": r0,
                "n_min": n1, "D_min": d1, "n_runner_up": n2,
                "D_runner_up": d2, "gap_abs": gap,
                "gap_rel_to_min": gap / abs(d1) if d1 else float("nan"),
                "spread_min": s1, "spread_runner_up": s2,
                "two_spread": 2.0 * u,
                "identifiable": int(math.isfinite(u) and gap > 2.0 * u),
            })
    out.sort(key=lambda r: (r["scheme"], r["Re"], r["N"],
                            r["delta_fraction"], r["r0"]))
    fields = ["scheme", "Re", "N", "delta_fraction", "r0", "n_min", "D_min",
              "n_runner_up", "D_runner_up", "gap_abs", "gap_rel_to_min",
              "spread_min", "spread_runner_up", "two_spread", "identifiable"]
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for r in out:
            w.writerow({k: r[k] for k in fields})
    return out


# ---------------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------------
MARKERS = {0.0: "o", 0.03125: "s", 0.0625: "^", 0.125: "v", 0.25: "D"}
LINES = {128: "-", 256: "--", 384: "-.", 512: ":"}
GREYS = ["0.15", "0.35", "0.55", "0.72", "0.88"]


def _style_axis(ax):
    ax.grid(True, color="0.9", lw=0.6)
    ax.tick_params(labelsize=8)
    ax.set_xlabel(ax.get_xlabel(), fontsize=9)
    ax.set_ylabel(ax.get_ylabel(), fontsize=9)
    ax.set_title(ax.get_title(), fontsize=10)


def make_sensitivity_figure(rows: list[dict], path: Path):
    fig, axes = plt.subplots(2, 2, figsize=(11.0, 7.6))
    prod = [r for r in rows if r["analysis_eligible"]
            and r["scheme"] == "production" and r["Re"] == 1000.0]

    ax = axes[0, 0]
    sub = [r for r in prod if r["n"] == 4.0 and r["N"] == 512]
    for i, r0 in enumerate(R0_VALUES):
        s = sorted((r for r in sub if r["r0"] == r0),
                   key=lambda r: r["delta_fraction"])
        ax.plot([r["delta_fraction"] for r in s], [r["D_core"] for r in s],
                marker=MARKERS[r0], color=GREYS[i], lw=1.5, ms=5,
                label=fr"$r_0={r0:g}$")
    ax.set(xlabel=r"$\delta/L_c$", ylabel=r"$D_{\delta,r_0}$",
           title="(a) n=4, N=512: wall thickness")
    ax.legend(fontsize=7, ncol=2, frameon=False)

    ax = axes[0, 1]
    sub = [r for r in prod if r["n"] == 4.0 and r["N"] == 512]
    for i, frac in enumerate(DELTA_FRACTIONS):
        s = sorted((r for r in sub if r["delta_fraction"] == frac),
                   key=lambda r: r["r0"])
        ax.plot([r["r0"] for r in s], [r["D_core"] for r in s],
                marker=["o", "s", "^"][i], color=GREYS[i], lw=1.5, ms=5,
                label=fr"$\delta/L_c={frac:g}$")
    ax.set(xlabel=r"$r_0$", ylabel=r"$D_{\delta,r_0}$",
           title="(b) n=4, N=512: junction radius")
    ax.legend(fontsize=7, frameon=False)

    ax = axes[1, 0]
    sub = [r for r in prod if r["delta_fraction"] == 0.05
           and r["r0"] == 0.0625]
    for i, n in enumerate((2.0, 4.0, 8.0)):
        s = sorted((r for r in sub if r["n"] == n), key=lambda r: r["N"])
        ax.plot([r["N"] for r in s], [r["D_core"] for r in s],
                marker=["o", "s", "^"][i], color=GREYS[i], lw=1.4, ms=5,
                label=fr"$n={n:g}$")
    ax.set(xlabel="$N$", ylabel=r"$D_{\delta,r_0}$",
           title="(c) Delta=0.05L_c, r0=0.0625")
    ax.legend(fontsize=7, frameon=False)

    ax = axes[1, 1]
    s = sorted((r for r in prod if r["n"] in (2.0, 4.0)
                and r["N"] == 512 and r["delta_fraction"] == 0.05),
               key=lambda r: (r["r0"], r["n"]))
    by_r0 = defaultdict(dict)
    for r in s:
        by_r0[r["r0"]][round(r["n"], 9)] = r["D_core"]
    for i, r0 in enumerate(R0_VALUES):
        if 2.0 not in by_r0[r0] or 4.0 not in by_r0[r0]:
            continue
        ax.plot(r0, by_r0[r0][4.0] - by_r0[r0][2.0],
                marker=MARKERS[r0], color="0.2", lw=0, ms=7)
    ax.set(xlabel=r"$r_0$", ylabel=r"$\Delta D(4-2)$",
           title="(d) Re=1000, N=512, Delta=0.05L_c")
    ax.axhline(0.0, color="0.6", lw=0.8)

    for ax in axes.flat:
        _style_axis(ax)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def make_paired_figure(paired: list[dict], path: Path):
    fig, axes = plt.subplots(2, 2, figsize=(11.0, 7.6))
    base = [r for r in paired if r["scheme"] == "production"
            and r["Re"] == 1000.0 and r["pair_kind"] == "focus"]

    ax = axes[0, 0]
    for i, frac in enumerate(DELTA_FRACTIONS):
        s = sorted([r for r in base if r["n_i"] == 2.0 and r["n_j"] == 4.0
                    and r["r0"] == 0.0625 and r["delta_fraction"] == frac],
                   key=lambda r: r["N"])
        if s:
            ax.plot([r["N"] for r in s], [r["delta_D"] for r in s],
                    marker=["o", "s", "^"][i], color=GREYS[i], lw=1.4, ms=5,
                    label=fr"$\delta/L_c={frac:g}$")
    ax.set(xlabel="$N$", ylabel=r"$\Delta D(4-2)$",
           title="(a) D2-D4, r0=0.0625")
    ax.legend(fontsize=7, frameon=False)

    ax = axes[0, 1]
    for i, frac in enumerate(DELTA_FRACTIONS):
        s = sorted([r for r in base if r["n_i"] == 4.0 and r["n_j"] == 8.0
                    and r["r0"] == 0.0625 and r["delta_fraction"] == frac],
                   key=lambda r: r["N"])
        if s:
            ax.plot([r["N"] for r in s], [r["delta_D"] for r in s],
                    marker=["o", "s", "^"][i], color=GREYS[i], lw=1.4, ms=5,
                    label=fr"$\delta/L_c={frac:g}$")
    ax.set(xlabel="$N$", ylabel=r"$\Delta D(4-8)$",
           title="(b) D4-D8, r0=0.0625")
    ax.legend(fontsize=7, frameon=False)

    ax = axes[1, 0]
    for i, pair in enumerate(((3.0, 4.0), (4.0, 5.0))):
        s = sorted([r for r in base if (r["n_i"], r["n_j"]) == pair
                    and r["r0"] == 0.0625 and r["delta_fraction"] == 0.05],
                   key=lambda r: r["N"])
        if s:
            ax.plot([r["N"] for r in s], [r["delta_D"] for r in s],
                    marker=["o", "s"][i], color=GREYS[i], lw=1.4, ms=5,
                    label=fr"$\Delta D({pair[0]:g}-{pair[1]:g})$")
    ax.set(xlabel="$N$", ylabel=r"$\Delta D$",
           title="(c) neighbors at Delta=0.05L_c")
    ax.legend(fontsize=7, frameon=False)

    ax = axes[1, 1]
    for i, pair in enumerate(((2.0, 4.0), (4.0, 8.0))):
        s = sorted([r for r in base if (r["n_i"], r["n_j"]) == pair
                    and r["N"] == 512 and r["delta_fraction"] == 0.05],
                   key=lambda r: r["r0"])
        if s:
            ax.plot([r["r0"] for r in s], [r["delta_D"] for r in s],
                    marker=["o", "s"][i], color=GREYS[i], lw=1.4, ms=5,
                    label=fr"$\Delta D({pair[0]:g}-{pair[1]:g})$")
    ax.set(xlabel=r"$r_0$", ylabel=r"$\Delta D$",
           title="(d) N=512, Delta=0.05L_c")
    ax.legend(fontsize=7, frameon=False)

    for ax in axes.flat:
        ax.axhline(0.0, color="0.65", lw=0.7)
        _style_axis(ax)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def make_stability_figure(stability: list[dict], path: Path):
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    s = sorted([r for r in stability if r["scheme"] == "production"
                and r["Re"] == 1000.0 and r["delta_fraction"] == 0.05
                and r["r0"] == 0.0625], key=lambda r: r["N"])
    if s:
        ax.plot([r["N"] for r in s], [r["gap_abs"] for r in s], "o-",
                color="0.15", lw=1.5, ms=6, label="gap to runner-up")
        ax.plot([r["N"] for r in s], [r["two_spread"] for r in s], "s--",
                color="0.45", lw=1.4, ms=6, label=r"$2\times$ resolution spread")
    ax.set(xlabel="$N$", ylabel=r"$D$ difference",
           title="Minimum depth vs numerical spread (Re=1000, Delta=0.05L_c, r0=0.0625)")
    ax.legend(fontsize=8, frameon=False)
    _style_axis(ax)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def make_annulus_figure(annuli: list[dict], path: Path):
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.3))
    for j, (key, ylab) in enumerate((("D_annulus", r"$D_j(r,2r)$"),
                                     ("mean_r_S", r"$\langle r|S|\rangle$"))):
        ax = axes[j]
        for N in (128, 256, 384, 512):
            s = sorted([a for a in annuli if a["n"] == 4.0 and a["N"] == N],
                       key=lambda a: a["r"])
            # sum over the two junctions
            by_r = defaultdict(float)
            for a in s:
                by_r[a["r"]] += a[key]
            if not by_r:
                continue
            ax.plot([math.log(r) for r in sorted(by_r)],
                    [by_r[r] for r in sorted(by_r)],
                    marker="os^D"[(128, 256, 384, 512).index(N)],
                    color=GREYS[(128, 256, 384, 512).index(N)],
                    linestyle=LINES[N], lw=1.4, ms=5, label=f"N={N}")
        ax.set(xlabel=r"$\ln r$", ylabel=ylab,
               title=("(a) annular dissipation" if j == 0
                      else "(b) local strain scaling"))
        ax.legend(fontsize=7, frameon=False)
        _style_axis(ax)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------
def write_report(rows, stability, annuli, path: Path):
    prod_primary = [r for r in rows if r["analysis_eligible"]
                    and r["scheme"] == "production"]
    n_geom = len({round(r["n"], 9) for r in prod_primary})
    n_re = len({r["Re"] for r in prod_primary})
    n_ns = sorted({r["N"] for r in prod_primary})
    stable = [r for r in stability
              if r["scheme"] == "production" and r["identifiable"]]
    frac_stable = 100.0 * len(stable) / len(stability) if stability else float("nan")
    max_res = max(abs(r["additivity_residual"]) for r in rows) if rows else 0.0
    lines = [
        "# Campagne A -- supports physiques fixes",
        "",
        "Aucune nouvelle simulation n'a ete lancee. Tous les champs macroscopiques",
        "archives presentant `ux, uy, fluid, X, Y, N, Re, n` ont ete releves.",
        "",
        f"- champs inscrits dans le CSV : {len(rows)//(len(DELTA_FRACTIONS)*len(R0_VALUES))}",
        f"- champs de production primaires : {len(prod_primary)//(len(DELTA_FRACTIONS)*len(R0_VALUES))}",
        f'- geometries : {n_geom}, Reynolds : {n_re}, grilles : '
        + ", ".join(str(int(N)) for N in n_ns),
        f"- sommes de repetition : addsitivite D_core+D_wall=D_base, residu max {max_res:.2e}",
        "",
        "## Definitions",
        "",
        r"$M_{r_0}=M_{\rm valid}\cap_j\{|\mathbf x-\mathbf x_j|>r_0\}$,",
        r"$M_{\delta,r_0}=M_{r_0}\cap\{d(\mathbf x,\Gamma_n)>\delta\}$.",
        r"$d$ est la distance euclidienne au bord superelliptique exact, echantillonne",
        f"par `Superellipse.boundary_points({N_BOUNDARY}, arc_uniform=True)` et interroge",
        "par KD-tree en coordonnees physiques. Le mur est le complement de",
        r"$M_{\delta,r_0}$ dans $M_{r_0}$ : $D_{\rm core}+D_{\rm wall}=D_{\rm base}$ exactement.",
        r"$h_N=2/(N-1)$ et $D=2\sum_M(S_{\rm lbm}:S_{\rm lbm}/Re)h_N^2$.",
        "Cette derniere convention est celle des tables deja publiees; elle est",
        "proportionnelle a la dissipation physique et permet la comparaison directe.",
        "",
        "## Schemes",
        "",
        "`production`, `diffusive`, `projected`, `snapshot`, `smoke` et `checkpoint`",
        "sont etiques dans le CSV. Les differences appariees n'utilisent que les",
        "champs `production` primaires; l'echelle diffusive reste un ladder distinct.",
        "Les doublons (memes n, Re, N) sont marques `primary=0` selon la priorite",
        "des archives figees (`data`, `data_all190`, puis grilles de convergence).",
        "",
        "## Resultats structurels",
        "",
        f"- {len(stability)} lignes de stabilite de minimum; {frac_stable:.1f}% presentent",
        "  un creux superieur a deux fois l'ecart maximal entre grilles consecutives.",
        "- La conclusion finale sur l'optimum ne doit etre conservee que si ce test",
        "  reste vrai pour plusieurs supports et aux grilles fines.",
        f"- {len(annuli)} mesures de couronnes de jonction ont ete ajoutees pour",
        "  preparer la Campagne B; elles ne prouvent pas a elles seules la singularite.",
        "",
        "## Figures",
        "",
        "Voir `figures/campaign_a/` et `figures/campaign_a/alt_text_campaign_A.txt`.",
        "Toutes les figures sont en niveaux de gris avec marqueurs et styles de",
        "ligne distincts, donc lisibles en noir et blanc.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


ALT_TEXTS = [
    ("fig_campaign_a_delta_r0_sensitivity.png",
     "Panels (a)-(b): production-scaled dissipation at n=4, Re=1000 and N=512 "
     "versus wall thickness delta/Lc and junction radius r0. Panel (c): "
     "dissipation at delta/Lc=0.05 and r0=0.0625 against N for n=2, 4 and 8. "
     "Panel (d): paired difference D(4)-D(2) against r0 at N=512. Symbols and "
     "line styles distinguish parameter values in black and white."),
    ("fig_campaign_a_paired_differences.png",
     "Paired geometry differences of fixed-support dissipation at Re=1000. "
     "Panels (a)-(b): D(2)-D(4) and D(4)-D(8) versus N for three wall "
     "thicknesses. Panel (c): differences between neighboring exponents at "
     "delta/Lc=0.05. Panel (d): differences versus junction radius at N=512. "
     "The zero line is shown; no sign reversal is imposed."),
    ("fig_campaign_a_minimum_stability.png",
     "Gap between the lowest and second-lowest sampled geometry versus N at "
     "Re=1000, delta/Lc=0.05 and r0=0.0625, compared with twice the largest "
     "consecutive-grid resolution spread. A minimum is called identifiable only "
     "when the gap exceeds this numerical scale."),
    ("fig_campaign_a_junction_annuli.png",
     "Annular viscous dissipation around the two tangential-lid junctions and "
     "mean r|S| versus ln r for n=4 and Re=1000 at N=128, 256, 384 and 512. "
     "Distinct greys, markers and line styles encode the resolution. The "
     "innermost annuli are limited by the five-point gradient-valid mask."),
]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    t0 = time.time()
    OUT_DATA.mkdir(parents=True, exist_ok=True)
    OUT_FIG.mkdir(parents=True, exist_ok=True)

    fields = scan_fields()
    print(f"[A] inventoried {len(fields)} final fields "
          f"({sum(r['primary'] for r in fields)} primary)", flush=True)

    csv_rows = []
    annulus_inputs = []
    for i, rec in enumerate(fields, 1):
        field = read_field(rec)
        csv_rows.extend(analyse_field(field))
        if is_annulus_case(field):
            annulus_inputs.append(field)
        if i % 100 == 0 or i == len(fields):
            print(f"[A] analysed {i}/{len(fields)} fields "
                  f"({time.time()-t0:.1f}s)", flush=True)

    fields_out = ["scheme", "primary", "analysis_eligible", "source",
                  "case_name", "n", "Re", "N", "h", "U_lid", "nu_lbm",
                  "tau_lbm", "L_c", "delta_fraction", "delta", "r0",
                  "n_core", "n_wall", "A_core", "A_wall", "D_base",
                  "D_core", "D_wall", "q_core", "additivity_residual"]
    diss_path = OUT_DATA / "campaign_a_dissipation.csv"
    with diss_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields_out)
        w.writeheader()
        for r in csv_rows:
            w.writerow({k: r[k] for k in fields_out})

    paired = write_paired_differences(
        csv_rows, OUT_DATA / "campaign_a_paired_differences.csv")
    stability = write_minimum_stability(
        csv_rows, OUT_DATA / "campaign_a_minimum_stability.csv")

    annuli = annulus_diagnostics(annulus_inputs)
    ann_path = OUT_DATA / "campaign_a_annuli.csv"
    ann_fields = ["n", "Re", "N", "junction", "r", "ln_r", "n_cells",
                  "D_annulus", "mean_r_S", "max_r_S", "source"]
    with ann_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=ann_fields)
        w.writeheader()
        for a in annuli:
            w.writerow({k: a[k] for k in ann_fields})

    make_sensitivity_figure(
        csv_rows, OUT_FIG / "fig_campaign_a_delta_r0_sensitivity.png")
    make_paired_figure(
        paired, OUT_FIG / "fig_campaign_a_paired_differences.png")
    make_stability_figure(
        stability, OUT_FIG / "fig_campaign_a_minimum_stability.png")
    make_annulus_figure(
        annuli, OUT_FIG / "fig_campaign_a_junction_annuli.png")
    (OUT_FIG / "alt_text_campaign_A.txt").write_text(
        "\n\n".join(f"{name}: {text}" for name, text in ALT_TEXTS) + "\n",
        encoding="utf-8")
    write_report(csv_rows, stability, annuli,
                 OUT_DATA / "README_campaign_A.md")

    print(f"[A] rows={len(csv_rows)} paired={len(paired)} "
          f"stability={len(stability)} annuli={len(annuli)}", flush=True)
    print(f"[A] done in {time.time()-t0:.1f}s -> {OUT_DATA}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
