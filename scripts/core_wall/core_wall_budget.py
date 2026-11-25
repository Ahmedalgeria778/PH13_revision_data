# -*- coding: utf-8 -*-
"""Additive core/wall dissipation budget on the production gradient-valid mask.

For each case the gradient-valid mask M is partitioned as
    W_delta = M & {dist(x, Gamma) <= delta},   C_delta = M \\ W_delta,
so that W_delta and C_delta are disjoint and W_delta U C_delta = M exactly.
With phi = (1/Re)*2S:S and D = 2*sum_M(phi)*dx^2 (nu = 2/Re):

    D_mask / A_mask = D_wall / A_mask + D_core / A_mask.

All three terms use the SAME denominator A_mask, as requested by referee #4.3.
No new simulation: archived N=128 (190-case grid) and N=256 (63-case) fields.
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

import numpy as np
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
D128 = ROOT / "05_dataset" / "data_all190"
D256_DIRS = (ROOT / "05_dataset" / "data_conv256", ROOT / "05_dataset" / "data_conv256_lowRe")
DELTAS = (0.025, 0.05)


def gradient_valid_mask(fluid):
    v = np.zeros_like(fluid, dtype=bool)
    v[1:-1, 1:-1] = (fluid[1:-1, 1:-1] & fluid[:-2, 1:-1] & fluid[2:, 1:-1]
                     & fluid[1:-1, :-2] & fluid[1:-1, 2:])
    return v


def phi_field(ux, uy, fluid, re, dx, valid):
    g = [np.full(ux.shape, np.nan) for _ in range(4)]
    g[0][1:-1, 1:-1] = (ux[1:-1, 2:] - ux[1:-1, :-2]) / (2.0 * dx)
    g[1][1:-1, 1:-1] = (uy[1:-1, 2:] - uy[1:-1, :-2]) / (2.0 * dx)
    g[2][1:-1, 1:-1] = (ux[2:, 1:-1] - ux[:-2, 1:-1]) / (2.0 * dx)
    g[3][1:-1, 1:-1] = (uy[2:, 1:-1] - uy[:-2, 1:-1]) / (2.0 * dx)
    ux_x, uy_x, ux_y, uy_y = g
    phi = (2.0 * ux_x**2 + 2.0 * uy_y**2 + (ux_y + uy_x)**2) / re
    return np.where(valid, phi, 0.0)


def analyse(path):
    with np.load(path) as z:
        n, re, N = float(z["n"]), float(z["Re"]), int(z["N"])
        ux, uy = np.asarray(z["ux"], float), np.asarray(z["uy"], float)
        fluid = np.asarray(z["fluid"]).astype(bool)
        xx = np.asarray(z["X"], float)
        dx = float(abs(xx[0, 1] - xx[0, 0]))
        lc = float(z["L_char"]) * dx
        cid = str(z["case_id"])
    valid = gradient_valid_mask(fluid)
    phi = phi_field(ux, uy, fluid, re, dx, valid)
    cell = dx * dx
    Amask = float(np.count_nonzero(valid)) * cell
    Dmask = 2.0 * float(np.sum(phi)) * cell
    dist = ndimage.distance_transform_edt(fluid) * dx

    rows = []
    for frac in DELTAS:
        wall = valid & (dist <= frac * lc)
        core = valid & (~wall)
        Dw = 2.0 * float(np.sum(np.where(wall, phi, 0.0))) * cell
        Dc = 2.0 * float(np.sum(np.where(core, phi, 0.0))) * cell
        rows.append(dict(case_id=cid, n=n, Re=re, N=N, delta_over_Lc=frac,
                         A_mask=Amask, D_mask=Dmask,
                         D_wall=Dw, D_core=Dc,
                         Dmask_over_A=Dmask / Amask,
                         Dwall_over_A=Dw / Amask, Dcore_over_A=Dc / Amask,
                         A_wall=float(np.count_nonzero(wall)) * cell,
                         A_core=float(np.count_nonzero(core)) * cell,
                         f_wall=Dw / Dmask, f_core=Dc / Dmask,
                         additivity_residual=Dmask - (Dw + Dc)))
    return rows


def collect():
    paths = {}
    for p in D128.glob("*.npz"):
        with np.load(p) as z:
            key = (round(float(z["n"]), 4), round(float(z["Re"]), 1), 128)
        paths[key] = p
    for d in D256_DIRS:
        for p in d.glob("*.npz"):
            with np.load(p) as z:
                if "N" not in z.files or int(z["N"]) != 256:
                    continue
                key = (round(float(z["n"]), 4), round(float(z["Re"]), 1), 256)
            paths[key] = p
    return paths


def main():
    paths = collect()
    print("cases found: N=128:", sum(1 for k in paths if k[2] == 128),
          "N=256:", sum(1 for k in paths if k[2] == 256))
    rows = []
    for k in sorted(paths):
        rows.extend(analyse(paths[k]))
    with (OUT / "core_wall_budget.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    maxres = max(abs(r["additivity_residual"]) for r in rows)
    print("rows:", len(rows), " max |D_mask-(D_wall+D_core)| =", maxres)

    # summary for the three requested Reynolds numbers
    for N in (128, 256):
        for frac in DELTAS:
            print("\n=== N=%d  delta=%.3f Lc : D/A_mask = D_wall/A_mask + D_core/A_mask ===" % (N, frac))
            print("   n    Re       D/A       wall/A     core/A     f_wall   f_core")
            for Re in (300.0, 500.0, 1000.0):
                sub = sorted((r for r in rows if r["N"] == N and r["Re"] == Re
                              and abs(r["delta_over_Lc"] - frac) < 1e-12),
                             key=lambda r: r["n"])
                for r in sub:
                    print("  %5.2f %6.0f  %9.6f  %9.6f  %9.6f   %.4f    %.4f"
                          % (r["n"], r["Re"], r["Dmask_over_A"], r["Dwall_over_A"],
                             r["Dcore_over_A"], r["f_wall"], r["f_core"]))
                print()


if __name__ == "__main__":
    main()
