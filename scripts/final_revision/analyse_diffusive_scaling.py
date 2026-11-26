# -*- coding: utf-8 -*-
"""Compare the production and diffusive n=4, Re=1000 dissipation ladders.

The diffusive campaign uses U_lid(N) = 0.05*128/N, keeping nu_lbm and tau
essentially fixed while lowering the lattice Mach number as 1/N.  This script
recomputes the production values from the archived fields, reads the converged
diffusive values from results_diffusive/diffusive_scaling.csv, and writes a
compact comparison table plus increment/order diagnostics.

Outputs:
    06_physics/results_diffusive/diffusive_comparison.csv
    06_physics/results_diffusive/diffusive_comparison.md
"""
from __future__ import annotations

import csv
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
from etude_convergence_paroi import gradient_valid_mask  # noqa: E402

RES = HERE / "results_diffusive"
R0 = (0.0, 0.25, 0.5)
NS = (128, 256, 384)
N_REF = 128
U_REF = 0.05
RE = 1000.0
JUNC = ((1.0, 0.0), (-1.0, 0.0))

PROD_FILES = {
    128: ROOT / "05_dataset/data_all190/se_n4p0_Re1000_N128.npz",
    256: ROOT / "05_dataset/data_conv256/se_n4p0_Re1000_N256.npz",
    384: ROOT / "05_dataset/data_convHR/se_n4p0_Re1000_N384.npz",
}
DIFF_FILES = {
    N: ROOT / "05_dataset/data_diffusive" / f"se_n4p0_Re1000_N{N}_diffusive.npz"
    for N in NS
}


def u_lid(N: int) -> float:
    return U_REF * N_REF / N


def dissipation(path: Path) -> dict[str, float]:
    with np.load(path) as z:
        ux = np.asarray(z["ux"], float)
        uy = np.asarray(z["uy"], float)
        fluid = np.asarray(z["fluid"]).astype(bool)
        xx = np.asarray(z["X"], float)
        yy = np.asarray(z["Y"], float)
        N = int(z["N"])
        Re = float(z["Re"])
    dx = float(abs(xx[0, 1] - xx[0, 0]))
    valid = gradient_valid_mask(fluid)
    gx = np.full(ux.shape, np.nan)
    gy = np.full(ux.shape, np.nan)
    vx = np.full(ux.shape, np.nan)
    vy = np.full(ux.shape, np.nan)
    gx[1:-1, 1:-1] = (ux[1:-1, 2:] - ux[1:-1, :-2]) / (2 * dx)
    vx[1:-1, 1:-1] = (uy[1:-1, 2:] - uy[1:-1, :-2]) / (2 * dx)
    gy[1:-1, 1:-1] = (ux[2:, 1:-1] - ux[:-2, 1:-1]) / (2 * dx)
    vy[1:-1, 1:-1] = (uy[2:, 1:-1] - uy[:-2, 1:-1]) / (2 * dx)
    phi = (2 * gx**2 + 2 * vy**2 + (gy + vx) ** 2) / Re
    phi = np.where(valid, phi, 0.0)
    cell = dx * dx
    out = {"h": dx}
    for r0 in R0:
        keep = valid.copy()
        for xj, yj in JUNC:
            keep &= np.hypot(xx - xj, yy - yj) > r0
        out[f"D{r0:g}"] = 2.0 * float(np.sum(phi[keep])) * cell
    return out


def observed_order(d1: float, d2: float, d3: float) -> float:
    """Fit D(N)=D_inf+C*h^p to N=128,256,384 (grid ratios 2 and 1.5)."""
    inc12 = d2 - d1
    inc23 = d3 - d2
    if inc12 <= 0 or inc23 <= 0:
        return float("nan")
    target = inc12 / inc23

    def ratio(p: float) -> float:
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


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    prod = {N: dissipation(p) for N, p in PROD_FILES.items()}
    diff = {N: dissipation(p) for N, p in DIFF_FILES.items()}
    for N, p in DIFF_FILES.items():
        if not p.exists():
            print(f"[diffusive] missing {p}")
            return 1

    csv_path = RES / "diffusive_comparison.csv"
    fields = ["N", "h", "U_lid", "tau"]
    for r0 in R0:
        fields += [f"D_prod_r{r0:g}", f"D_diff_r{r0:g}",
                   f"ratio_diff_over_prod_r{r0:g}"]
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for N in NS:
            row = {"N": N, "h": prod[N]["h"], "U_lid": u_lid(N),
                   "tau": 3.0 * u_lid(N) * (N - 1) / RE + 0.5}
            for r0 in R0:
                key = f"D{r0:g}"
                dp, dd = prod[N][key], diff[N][key]
                row[f"D_prod_r{r0:g}"] = dp
                row[f"D_diff_r{r0:g}"] = dd
                row[f"ratio_diff_over_prod_r{r0:g}"] = dd / dp
            w.writerow(row)

    lines = [
        "# Diffusive-scaling check for n=4, Re=1000",
        "",
        "U_lid(N) = 0.05*128/N; nu_lbm and tau are kept nearly fixed while the",
        "lattice Mach number decreases as 1/N. All D values use the same",
        "gradient-valid quadrature and physical junction radii.",
        "",
        "| N | U_lid | tau | D_prod(r0=0) | D_diff(r0=0) | D_prod(r0=0.5) | "
        "D_diff(r0=0.5) |",
        "|---|---|---|---|---|---|---|",
    ]
    for N in NS:
        lines.append(
            f"| {N} | {u_lid(N):.6f} | {3*u_lid(N)*(N-1)/RE+0.5:.6f} | "
            f"{prod[N]['D0']:.6f} | {diff[N]['D0']:.6f} | "
            f"{prod[N]['D0.5']:.6f} | {diff[N]['D0.5']:.6f} |")
    lines += ["", "## Increment diagnostics", ""]
    for r0 in R0:
        key = f"D{r0:g}"
        dp = [prod[N][key] for N in NS]
        dd = [diff[N][key] for N in NS]
        ip = [dp[1] - dp[0], dp[2] - dp[1]]
        idd = [dd[1] - dd[0], dd[2] - dd[1]]
        p_prod = observed_order(*dp)
        p_diff = observed_order(*dd)
        lines += [
            f"- r0={r0:g}: production increments {ip[0]:.6f}, {ip[1]:.6f} "
            f"(ratio {ip[1]/ip[0]:.3f}); diffusive increments "
            f"{idd[0]:.6f}, {idd[1]:.6f} (ratio {idd[1]/idd[0]:.3f}).",
            f"  Observed order fitted to the 128/256/384 increments: "
            f"production {p_prod:.2f}; diffusive {p_diff:.2f}.",
        ]
    lines += [
        "",
        "The N=128 fields agree by construction because U_lid and tau match.",
        "The comparison tests only whether lowering the lattice Mach number",
        "changes the remaining drift; it is not a continuum certification.",
        "",
    ]
    md_path = RES / "diffusive_comparison.md"
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    print(f"[diffusive] wrote {csv_path.name} and {md_path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
