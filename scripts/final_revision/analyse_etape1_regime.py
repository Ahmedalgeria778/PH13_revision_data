# -*- coding: utf-8 -*-
"""
06_physics/analyse_etape1_regime.py

Etape 1 (spec referee) : trancher entre divergence en ln N et convergence
lente, en ajoutant la resolution N=512 (etude des coins) au cas
n=8, Re=1000, qui existe a N = 64, 128, 256, 512.

On calcule D(r0) pour r0 in {0, 0.125, 0.25, 0.5} (rayons physiques) aux
cinq resolutions disponibles (N=64,128,256,384,512), puis les increments
sur les doublements égaux :

    inc1 = D128 - D64
    inc2 = D256 - D128
    inc3 = D512 - D256

et les rapports inc2/inc1, inc3/inc2, les ordres observés et les limites de
Richardson. Le point N=384 est rapporté mais n'entre pas dans les rapports
de doublement.

    inc3/inc2 ~ 0.9  -> divergence en ln N (pas de limite)
    inc3/inc2 -> 0.5 -> convergence d'ordre ~1 (extrapolation possible)

Sorties : 06_physics/results_regime/
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
from etude_convergence_paroi import gradient_valid_mask  # noqa: E402

ALL190 = _ROOT / "05_dataset" / "data_all190"
CONV = _ROOT / "05_dataset" / "data_conv"
CONV256 = _ROOT / "05_dataset" / "data_conv256"
CONVHR = _ROOT / "05_dataset" / "data_convHR"
OUT_DIR = _HERE / "results_regime"

CASE = (8.0, 1000.0)
R0 = (0.0, 0.125, 0.25, 0.5)
JUNCTIONS = ((1.0, 0.0), (-1.0, 0.0))
NS = (64, 128, 256, 384, 512)


def case_id(n, Re, N):
    return f"se_n{str(round(n, 2)).replace('.', 'p')}_Re{int(round(Re))}_N{N}"


def find_file(n, Re, N):
    cid = case_id(n, Re, N)
    cand = {64: (CONV,), 128: (ALL190,), 256: (CONV256, CONV),
            384: (CONVHR,), 512: (CONVHR,)}.get(N, ())
    for d in cand:
        p = d / f"{cid}.npz"
        if p.exists() and "_ckpt" not in p.name:
            return p
    for d in (CONV, CONV256, CONVHR, ALL190):
        p = d / f"{cid}.npz"
        if p.exists() and "_ckpt" not in p.name:
            return p
    return None


def analyse(path: Path) -> dict:
    with np.load(path) as z:
        n = float(z["n"]); Re = float(z["Re"]); N = int(z["N"])
        ux = np.asarray(z["ux"], float); uy = np.asarray(z["uy"], float)
        fluid = np.asarray(z["fluid"]).astype(bool)
        xx = np.asarray(z["X"], float); yy = np.asarray(z["Y"], float)
    dx = float(abs(xx[0, 1] - xx[0, 0]))
    valid = gradient_valid_mask(fluid)
    gx = np.full(ux.shape, np.nan); gy = np.full(uy.shape, np.nan)
    vx = np.full(ux.shape, np.nan); vy = np.full(uy.shape, np.nan)
    gx[1:-1, 1:-1] = (ux[1:-1, 2:] - ux[1:-1, :-2]) / (2 * dx)
    vx[1:-1, 1:-1] = (uy[1:-1, 2:] - uy[1:-1, :-2]) / (2 * dx)
    gy[1:-1, 1:-1] = (ux[2:, 1:-1] - ux[:-2, 1:-1]) / (2 * dx)
    vy[1:-1, 1:-1] = (uy[2:, 1:-1] - uy[:-2, 1:-1]) / (2 * dx)
    phi = (2 * gx ** 2 + 2 * vy ** 2 + (gy + vx) ** 2) / Re
    phi = np.where(valid, phi, 0.0)
    cell = dx * dx
    row = {"N": N, "h": dx}
    for r0 in R0:
        keep = valid.copy()
        for (xj, yj) in JUNCTIONS:
            keep &= np.hypot(xx - xj, yy - yj) > r0
        row[f"D_r{r0:g}"] = 2.0 * float(np.sum(phi[keep])) * cell
        row[f"A_r{r0:g}"] = float(np.count_nonzero(keep)) * cell
    return row


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    n, Re = CASE
    rows = []
    for N in NS:
        p = find_file(n, Re, N)
        if p is None:
            print(f"[etape1] MANQUE N={N}")
            continue
        r = analyse(p)
        r["source"] = str(p.relative_to(_ROOT))
        rows.append(r)
        print(f"[etape1] N={N} <- {p.name} OK", flush=True)

    byN = {r["N"]: r for r in rows}
    out = {"case": {"n": n, "Re": Re}, "r0": list(R0), "rows": rows,
           "increments": {}}
    lines = ["# Etape 1 — regime de D(N) pour n=8, Re=1000 "
             "(N=64/128/256/384/512)", "",
             "| r0 | D64 | D128 | D256 | D384 | D512 | inc1 | inc2 | inc3 | "
             "inc2/inc1 | inc3/inc2 | p1 | p2 | D_Richardson |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r0 in R0:
        k = f"D_r{r0:g}"
        vals = [byN[N][k] for N in NS if N in byN]
        if len(vals) < 5:
            continue
        d64, d128, d256, d384, d512 = vals
        inc1, inc2, inc3 = d128 - d64, d256 - d128, d512 - d256
        r21 = inc2 / inc1 if inc1 else float("nan")
        r32 = inc3 / inc2 if inc2 else float("nan")
        p1 = float(-np.log2(r21)) if r21 > 0 else float("nan")
        p2 = float(-np.log2(r32)) if r32 > 0 else float("nan")
        dinf = d512 + inc3 / (2.0 ** p2 - 1.0) if r32 > 0 and p2 > 0 else None
        out["increments"][f"r{r0:g}"] = {
            "D": vals, "inc1": inc1, "inc2": inc2, "inc3": inc3,
            "inc2_over_inc1": r21, "inc3_over_inc2": r32,
            "p_geometric_inc2_inc1": p1, "p_geometric_inc3_inc2": p2,
            "richardson_limit": dinf,
            "N512_shortfall": (dinf - d512) / dinf if dinf else None}
        rich = f"{dinf:.6f}" if dinf is not None else "n/a (log growth)"
        lines.append(
            f"| {r0:g} | {d64:.5f} | {d128:.5f} | {d256:.5f} | "
            f"{d384:.5f} | {d512:.5f} | {inc1:.3e} | {inc2:.3e} | "
            f"{inc3:.3e} | {r21:.3f} | {r32:.3f} | {p1:.2f} | "
            f"{p2:.2f} | {rich} |")

    (OUT_DIR / "etape1_regime.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8")
    with (OUT_DIR / "etape1_regime.csv").open("w", newline="",
                                              encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    (OUT_DIR / "etape1_resume.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
