# -*- coding: utf-8 -*-
"""Fixed-physical-wall-support dissipation diagnostic for n=4, Re=1000.

This script evaluates the production-family dissipation ladder on two
supports:

  M       : the gradient-valid mask used in the production post-processing;
  M_core  : M intersected with {dist(x, Gamma) > delta}, where dist is the
            distance to the exact superellipse boundary Gamma
            (n=4, a=b=1, L_c=2) and delta = 0.05 L_c or 0.10 L_c.

The boundary distance is obtained from a dense boundary sampling and a
KD-tree query in physical coordinates.  It is therefore independent of the
lattice resolution; a lattice distance-transform would reintroduce the O(h)
support error that this test is designed to isolate.

Outputs (inside PH13_revision_data):
    data/diffusive/dcore_fixed_wall.csv
    data/diffusive/dcore_fixed_wall.md
    supplement/dcore_fixed_wall_table.tex
"""
from __future__ import annotations

import csv
import math
import sys
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree

HERE = Path(__file__).resolve().parent


def _find_data_root(start: Path) -> Path:
    """Locate the directory containing 05_dataset (works from the package copy)."""
    for cand in (start,) + tuple(start.parents):
        if (cand / "05_dataset").is_dir():
            return cand
    return start.parent.parent


DATA_ROOT = _find_data_root(HERE)
PKG_ROOT = HERE.parent.parent
OUT_DIR = DATA_ROOT / "05_dataset" / "data_diffusive"
PKG_OUT_DIR = PKG_ROOT / "data" / "diffusive"
SUPP_OUT_DIR = PKG_ROOT / "supplement"

NS = (128, 256, 384, 512)
RE = 1000.0
N_EXP = 4.0
A = B = 1.0
L_C = 2.0
DELTA_FRACTIONS = (0.05, 0.10)
JUNC = ((1.0, 0.0), (-1.0, 0.0))
N_BOUNDARY = 300_000
R0_COMPARE = 0.5

PROD_FILES = {
    128: DATA_ROOT / "05_dataset/data_all190/se_n4p0_Re1000_N128.npz",
    256: DATA_ROOT / "05_dataset/data_conv256/se_n4p0_Re1000_N256.npz",
    384: DATA_ROOT / "05_dataset/data_convHR/se_n4p0_Re1000_N384.npz",
    512: DATA_ROOT / "05_dataset/data_convHR/se_n4p0_Re1000_N512.npz",
}


def gradient_valid_mask(fluid: np.ndarray) -> np.ndarray:
    """Five-point gradient-valid mask used by the production post-processing."""
    interior = np.zeros_like(fluid, dtype=bool)
    interior[1:-1, 1:-1] = (
        fluid[1:-1, 1:-1] & fluid[:-2, 1:-1] & fluid[2:, 1:-1]
        & fluid[1:-1, :-2] & fluid[1:-1, 2:]
    )
    return interior


def boundary_points(n_exp: float, a: float, b: float, count: int) -> np.ndarray:
    """Dense sampling of |x/a|^n + |y/b|^n = 1."""
    theta = np.linspace(0.0, 2.0 * math.pi, count, endpoint=False)
    c, s = np.cos(theta), np.sin(theta)
    x = a * np.sign(c) * np.abs(c) ** (2.0 / n_exp)
    y = b * np.sign(s) * np.abs(s) ** (2.0 / n_exp)
    return np.column_stack((x, y))


def exact_distance_to_boundary(xx, yy, boundary_tree) -> np.ndarray:
    """Distance from physical coordinates to the sampled exact boundary."""
    pts = np.column_stack((xx.ravel(), yy.ravel()))
    dist, _ = boundary_tree.query(pts, workers=-1)
    return dist.reshape(xx.shape)


def phi_field(ux, uy, fluid, dx, re):
    """Production strain-rate density phi = S:S / Re on the valid mask."""
    valid = gradient_valid_mask(fluid)
    gx = np.full(ux.shape, np.nan)
    gy = np.full(ux.shape, np.nan)
    vx = np.full(ux.shape, np.nan)
    vy = np.full(ux.shape, np.nan)
    gx[1:-1, 1:-1] = (ux[1:-1, 2:] - ux[1:-1, :-2]) / (2.0 * dx)
    vx[1:-1, 1:-1] = (uy[1:-1, 2:] - uy[1:-1, :-2]) / (2.0 * dx)
    gy[1:-1, 1:-1] = (ux[2:, 1:-1] - ux[:-2, 1:-1]) / (2.0 * dx)
    vy[1:-1, 1:-1] = (uy[2:, 1:-1] - uy[:-2, 1:-1]) / (2.0 * dx)
    phi = (2.0 * gx**2 + 2.0 * vy**2 + (gy + vx) ** 2) / re
    return np.where(valid, phi, 0.0), valid


def observed_order_fit(d128, d256, d384):
    """Fit D(N)=D_inf+C*h^p to N=128,256,384 (grid ratios 2 and 1.5)."""
    inc12 = d256 - d128
    inc23 = d384 - d256
    if inc12 <= 0 or inc23 <= 0:
        return float("nan")
    target = inc12 / inc23

    def ratio(p):
        return (2.0**p - 1.0) / (1.0 - (1.0 / 1.5) ** p)

    lo, hi = 1.0e-6, 20.0
    if target <= ratio(lo):
        return float("nan")
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if ratio(mid) < target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def equal_doubling_order(d128, d256, d512):
    inc1 = d256 - d128
    inc2 = d512 - d256
    if inc1 <= 0 or inc2 <= 0:
        return float("nan")
    return math.log2(inc1 / inc2)


def analyse_one(path: Path, tree) -> dict:
    with np.load(path) as z:
        ux = np.asarray(z["ux"], float)
        uy = np.asarray(z["uy"], float)
        fluid = np.asarray(z["fluid"]).astype(bool)
        xx = np.asarray(z["X"], float)
        yy = np.asarray(z["Y"], float)
        N = int(z["N"])
        re = float(z["Re"])
        n_exp = float(z["n"])
        l_c = float(z["L_c"])
        a = float(z["a"])
        b = float(z["b"])
    if not (abs(n_exp - N_EXP) < 1e-9 and abs(re - RE) < 1e-9
            and abs(l_c - L_C) < 1e-9 and abs(a - A) < 1e-9
            and abs(b - B) < 1e-9):
        raise ValueError(f"unexpected case metadata in {path}")
    dx = float(abs(xx[0, 1] - xx[0, 0]))
    phi, valid = phi_field(ux, uy, fluid, dx, re)
    dist = exact_distance_to_boundary(xx, yy, tree)
    cell = dx * dx

    out = {"N": N, "h": dx, "D_M": 2.0 * float(np.sum(phi[valid])) * cell}
    for frac in DELTA_FRACTIONS:
        delta = frac * l_c
        core = valid & (dist > delta)
        d_core = 2.0 * float(np.sum(phi[core])) * cell
        key = f"{frac:g}".replace(".", "p")
        out[f"D_core_{key}"] = d_core
        out[f"D_wall_{key}"] = out["D_M"] - d_core
        out[f"core_fraction_{key}"] = d_core / out["D_M"]
    keep_r0 = valid.copy()
    for xj, yj in JUNC:
        keep_r0 &= np.hypot(xx - xj, yy - yj) > R0_COMPARE
    out["D_r0p5"] = 2.0 * float(np.sum(phi[keep_r0])) * cell
    return out


def fmt(x, nd=6):
    return f"{x:.{nd}f}"


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    boundary = boundary_points(N_EXP, A, B, N_BOUNDARY)
    tree = cKDTree(boundary)
    rows = []
    for N in NS:
        path = PROD_FILES[N]
        if not path.exists():
            print(f"[dcore] missing {path}")
            return 1
        row = analyse_one(path, tree)
        rows.append(row)
        print(f"[dcore] N={N} D_M={row['D_M']:.6f} "
              f"D_core(0.05)={row['D_core_0p05']:.6f} "
              f"D_core(0.10)={row['D_core_0p1']:.6f} "
              f"D_r0.5={row['D_r0p5']:.6f}", flush=True)

    byN = {r["N"]: r for r in rows}
    for r in rows:
        for frac in DELTA_FRACTIONS:
            key = f"{frac:g}".replace(".", "p")
            residual = r["D_M"] - r[f"D_core_{key}"] - r[f"D_wall_{key}"]
            if abs(residual) > 1e-14:
                raise AssertionError(f"wall/core additivity failed: {residual}")
    orders = {}
    for col in ("D_r0p5", "D_core_0p05", "D_core_0p1"):
        vals = [byN[N][col] for N in NS]
        orders[col] = {
            "fit_128_256_384": observed_order_fit(*vals[:3]),
            "fit_128_256_512": observed_order_fit(vals[0], vals[1], vals[3]),
            "equal_128_256_512": equal_doubling_order(vals[0], vals[1], vals[3]),
            "rel_change_128_512": abs(vals[0] - vals[3]) / abs(vals[3]),
        }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    PKG_OUT_DIR.mkdir(parents=True, exist_ok=True)
    SUPP_OUT_DIR.mkdir(parents=True, exist_ok=True)

    fields = ["N", "h", "D_M"]
    for frac in DELTA_FRACTIONS:
        key = f"{frac:g}".replace(".", "p")
        fields += [f"D_core_{key}", f"D_wall_{key}", f"core_fraction_{key}"]
    fields += ["D_r0p5"]
    for p in (OUT_DIR, PKG_OUT_DIR):
        with (p / "dcore_fixed_wall.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            for r in rows:
                w.writerow({k: r[k] for k in fields})

    lines = [
        "# Fixed-physical-wall-support dissipation, n=4, Re=1000",
        "",
        "D_core(delta) = 2 nu sum_{M cap {dist>delta}} S:S dx^2, with dist the",
        "distance to the exact superellipse boundary (n=4, a=b=1, L_c=2).",
        "delta = 0.05 L_c = 0.10 and 0.10 L_c = 0.20. The boundary is sampled",
        f"with {N_BOUNDARY} points and queried with a KD tree in physical",
        "coordinates; the distance does not depend on the lattice spacing.",
        "",
        "| N | D_M | D_core(0.05 L_c) | D_core(0.10 L_c) | D_wall(0.05 L_c) | "
        "D_wall(0.10 L_c) | D_r0=0.5 |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['N']} | {fmt(r['D_M'])} | {fmt(r['D_core_0p05'])} | "
            f"{fmt(r['D_core_0p1'])} | {fmt(r['D_wall_0p05'])} | "
            f"{fmt(r['D_wall_0p1'])} | {fmt(r['D_r0p5'])} |")
    lines += ["", "## Orders and resolution sensitivity", "",
              "| quantity | fit 128/256/384 | fit 128/256/512 | "
              "equal-doubling 128/256/512 | |D_128-D_512|/|D_512| |",
              "|---|---|---|---|---|"]
    labels = {"D_r0p5": r"$D_{r_0=0.5}$",
              "D_core_0p05": r"$D_{\rm core}(0.05L_c)$",
              "D_core_0p1": r"$D_{\rm core}(0.10L_c)$"}
    for col, lab in labels.items():
        o = orders[col]
        def p(x):
            return f"{x:.2f}" if math.isfinite(x) else "n/a"
        lines.append(
            f"| {lab} | {p(o['fit_128_256_384'])} | "
            f"{p(o['fit_128_256_512'])} | {p(o['equal_128_256_512'])} | "
            f"{o['rel_change_128_512']*100:.1f}% |")
    lines += [
        "",
        "The fixed-support core values are nearly flat and decrease slightly;",
        "no positive fitted order is obtained from successive increments.",
        "D_core + D_wall = D_M is exact by construction. Orders and relative",
        "changes are diagnostics on archived grids, not continuum certifications.",
        "",
    ]
    for p in (OUT_DIR, PKG_OUT_DIR):
        (p / "dcore_fixed_wall.md").write_text("\n".join(lines), encoding="utf-8")

    tex = [
        "% Generated by scripts/final_revision/dcore_test.py",
        "\\begin{tabular}{@{}lcccccc@{}}",
        "\\toprule",
        "$N$ & $D_M$ & $D_{\\rm core}(0.05L_c)$ & $D_{\\rm core}(0.10L_c)$ "
        "& $D_{\\rm wall}(0.05L_c)$ & $D_{\\rm wall}(0.10L_c)$ \\\\",
        "\\midrule",
    ]
    for r in rows:
        tex.append(
            f"{r['N']} & {fmt(r['D_M'])} & {fmt(r['D_core_0p05'])} & "
            f"{fmt(r['D_core_0p1'])} & {fmt(r['D_wall_0p05'])} & "
            f"{fmt(r['D_wall_0p1'])} \\\\")
    tex += [
        "\\bottomrule",
        "\\end{tabular}",
    ]
    (SUPP_OUT_DIR / "dcore_fixed_wall_table.tex").write_text(
        "\n".join(tex) + "\n", encoding="utf-8")

    print("\n".join(lines))
    print(f"[dcore] wrote CSV/MD to {PKG_OUT_DIR}")
    print(f"[dcore] wrote table fragment to {SUPP_OUT_DIR / 'dcore_fixed_wall_table.tex'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
