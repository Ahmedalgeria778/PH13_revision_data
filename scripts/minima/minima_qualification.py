# -*- coding: utf-8 -*-
"""Traceable minima / crossing qualification for PH13.

Produces, from the archived fields only:

  case_metrics.csv       N, n, Re, D, A_mask, D/A_mask, A(n), file provenance
  fit_diagnostics.csv    argmin + 3-point and 5-point quadratic fits, supports,
                         exclusions, margins, estimator and validity flag
  crossing_diagnostics.csv  Re_c brackets for D(2.5)/D(3) and D/A(3)/D/A(4)
  minima_qualification_report.md

No simulation and no model training.  The production dissipation recipe is
reused verbatim: central differences on the gradient-valid fluid mask,
phi = (2 ux_x^2 + 2 uy_y^2 + (ux_y+uy_x)^2)/Re, D = 2 sum(phi) dx^2.
"""
from __future__ import annotations

import csv
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "01_geometry"))
from superellipse import Superellipse  # noqa: E402

DATA = ROOT / "05_dataset"
GROUPS = [
    ("N128_all190", ("data_all190",), 128),
    ("N128_refine", ("data_refine",), 128),
    ("N128_union", ("data_refine", "data_all190"), 128),
    ("N256_conv", ("data_conv256",), 256),
    ("N256_lowRe", ("data_conv256_lowRe",), 256),
    ("N256_union", ("data_conv256", "data_conv256_lowRe"), 256),
    ("N384_HR", ("data_convHR",), 384),
    ("N512_HR", ("data_convHR",), 512),
    ("N384_extB", ("data_convHR_extB",), 384),
    ("N512_extB", ("data_convHR_extB",), 512),
]
QUANTITIES = ("D_over_A_mask", "D")
FIT_K = (1, 2)   # 3-point and 5-point quadratic fits


def gradient_valid(fluid):
    v = np.zeros_like(fluid, dtype=bool)
    v[1:-1, 1:-1] = (fluid[1:-1, 1:-1] & fluid[:-2, 1:-1] & fluid[2:, 1:-1]
                     & fluid[1:-1, :-2] & fluid[1:-1, 2:])
    return v


def case_metrics(path):
    with np.load(path) as z:
        n, re = float(z["n"]), float(z["Re"])
        ux, uy = np.asarray(z["ux"], float), np.asarray(z["uy"], float)
        fluid = np.asarray(z["fluid"]).astype(bool)
        X = np.asarray(z["X"], float)
        dx = float(abs(X[0, 1] - X[0, 0]))
        a_exact = (float(z["area_exact"]) if "area_exact" in z.files
                   else Superellipse(n=n).area())
        cid = str(z["case_id"]) if "case_id" in z.files else path.stem
        N = int(z["N"]) if "N" in z.files else ux.shape[0]
        ux_x = np.full(ux.shape, np.nan); uy_x = np.full(ux.shape, np.nan)
        ux_y = np.full(ux.shape, np.nan); uy_y = np.full(ux.shape, np.nan)
        valid = gradient_valid(fluid)
        ux_x[1:-1, 1:-1] = (ux[1:-1, 2:] - ux[1:-1, :-2]) / (2 * dx)
        uy_x[1:-1, 1:-1] = (uy[1:-1, 2:] - uy[1:-1, :-2]) / (2 * dx)
        ux_y[1:-1, 1:-1] = (ux[2:, 1:-1] - ux[:-2, 1:-1]) / (2 * dx)
        uy_y[1:-1, 1:-1] = (uy[2:, 1:-1] - uy[:-2, 1:-1]) / (2 * dx)
        phi = np.where(valid, (2 * ux_x**2 + 2 * uy_y**2
                               + (ux_y + uy_x) ** 2) / re, 0.0)
        cell = dx * dx
        D = 2.0 * float(np.sum(phi)) * cell
        A_mask = float(np.count_nonzero(valid)) * cell
    return dict(case_id=cid, N=N, n=n, Re=re, D=D, A_mask=A_mask,
                D_over_A_mask=D / A_mask, A_exact=a_exact,
                D_over_A_exact=D / a_exact, n_valid=int(np.count_nonzero(valid)),
                dx=dx, source=path.parent.name, file=str(path.relative_to(ROOT)))


def load_cases():
    rows = []
    seen = set()
    # priority: refined grids overwrite coarse-grid duplicates at the same
    # (N, n, Re), because they are the locally refined versions of the case.
    priority = {"data_refine": 0, "data_all190": 1, "data_conv256": 0,
                "data_conv256_lowRe": 1, "data_convHR": 0,
                "data_convHR_extB": 1}
    paths = []
    for name in ("data_all190", "data_refine", "data_conv256",
                 "data_conv256_lowRe", "data_convHR", "data_convHR_extB"):
        for p in sorted((DATA / name).glob("*.npz")):
            paths.append(p)
    paths.sort(key=lambda p: (priority.get(p.parent.name, 9), str(p)))
    skipped = 0
    for p in paths:
        try:
            r = case_metrics(p)
        except (KeyError, ValueError):
            skipped += 1
            continue
        key = (r["N"], round(r["n"], 6), round(r["Re"], 6))
        if key in seen:
            continue
        seen.add(key)
        rows.append(r)
    if skipped:
        print("skipped archives without the standard metric keys:", skipped)
    return rows


def curve(rows, Re):
    sub = [r for r in rows if abs(r["Re"] - Re) < 1e-9]
    return sorted(sub, key=lambda r: r["n"])


def fit(rowset, quantity, k_side):
    """argmin + local OLS quadratic on k_side neighbours on each side."""
    pts = [(r["n"], r[quantity]) for r in rowset
           if math.isfinite(r[quantity])]
    if not pts:
        return None
    ns = np.array([p[0] for p in pts], float)
    ys = np.array([p[1] for p in pts], float)
    k = int(np.argmin(ys))
    left = ns[:k][-k_side:] if k_side else np.array([])
    right = ns[k + 1:][:k_side] if k_side else np.array([])
    support = np.concatenate([left, ns[k:k + 1], right])
    sel = np.isin(ns, support)
    x, y = ns[sel], ys[sel]
    out = dict(quantity=quantity, estimator=("OLS quadratic, %d points" % len(x)),
               n_argmin=float(ns[k]), y_argmin=float(ys[k]),
               n_support=";".join("%g" % v for v in x), n_support_points=int(len(x)),
               n_excluded=int(len(ns) - len(x)),
               a=None, n_star=None, y_star=None, margin_pct=None,
               valid=False, note="")
    if len(x) < 3:
        out["note"] = "fewer than 3 finite points in requested window"
        return out
    a, b, c = np.polyfit(x, y, 2)
    out["a"] = float(a)
    if a <= 0:
        out["note"] = "non-convex quadratic (a <= 0)"
        return out
    vertex = -b / (2 * a)
    if not (x.min() - 1e-9 <= vertex <= x.max() + 1e-9):
        out["note"] = "vertex outside fitted support"
        return out
    out["n_star"] = float(vertex)
    out["y_star"] = float(a * vertex**2 + b * vertex + c)
    out["valid"] = True
    best_other = min([v for n, v in zip(x, y)
                      if abs(n - ns[k]) > 1e-9], default=None)
    if best_other is not None and out["y_star"]:
        out["margin_pct"] = 100.0 * (best_other - out["y_star"]) / out["y_star"]
    return out


def crossing(rows, quantity, n1, n2, res_list):
    """Re where log(quantity(n1)) = log(quantity(n2)), linear in log."""
    vals = {}
    for Re in sorted(res_list):
        c = curve(rows, Re)
        a = next((r[quantity] for r in c if abs(r["n"] - n1) < 1e-9), None)
        b = next((r[quantity] for r in c if abs(r["n"] - n2) < 1e-9), None)
        if a is not None and b is not None and a > 0 and b > 0:
            vals[float(Re)] = (a, b)
    xs = sorted(vals)
    diff = [math.log(vals[x][0]) - math.log(vals[x][1]) for x in xs]
    for i in range(len(xs) - 1):
        if diff[i] * diff[i + 1] <= 0:
            t = -diff[i] / (diff[i + 1] - diff[i])
            return dict(estimator="linear interpolation of log-ratio",
                        n1=n1, n2=n2, Re_low=xs[i], Re_high=xs[i + 1],
                        Re_cross=xs[i] + t * (xs[i + 1] - xs[i]),
                        ratio_low=vals[xs[i]][0] / vals[xs[i]][1],
                        ratio_high=vals[xs[i + 1]][0] / vals[xs[i + 1]][1],
                        n_bracket_points=len(xs))
    return dict(estimator="linear interpolation of log-ratio", n1=n1, n2=n2,
                Re_low=None, Re_high=None, Re_cross=None,
                ratio_low=(vals[xs[0]][0] / vals[xs[0]][1] if xs else None),
                ratio_high=(vals[xs[-1]][0] / vals[xs[-1]][1] if xs else None),
                n_bracket_points=len(xs))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    all_rows = load_cases()
    case_fields = ["case_id", "source", "N", "n", "Re", "D", "A_mask",
                   "D_over_A_mask", "A_exact", "D_over_A_exact", "n_valid",
                   "dx", "file"]
    with (OUT / "case_metrics.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=case_fields)
        w.writeheader()
        for r in sorted(all_rows, key=lambda r: (r["N"], r["Re"], r["n"], r["source"])):
            w.writerow({k: ("%.12g" % r[k] if isinstance(r[k], float) else r[k])
                        for k in case_fields})

    fit_rows = []
    cross_rows = []
    group_data = {}
    for label, sources, N in GROUPS:
        sub = [r for r in all_rows if r["N"] == N and r["source"] in sources]
        group_data[label] = sub
        res_list = sorted(set(r["Re"] for r in sub))
        for Re in res_list:
            c = curve(sub, Re)
            for q in QUANTITIES:
                for k in FIT_K:
                    f = fit(c, q, k)
                    if f is None:
                        continue
                    fit_rows.append(dict(group=label, N=N, Re=Re,
                                         n_cases=len(c), **f))
        for q, n1, n2 in (("D", 2.5, 3.0), ("D_over_A_mask", 3.0, 4.0)):
            cr = crossing(sub, q, n1, n2, res_list)
            cross_rows.append(dict(group=label, N=N, quantity=q, **cr))

    fit_fields = ["group", "N", "Re", "n_cases", "quantity", "estimator",
                  "n_argmin", "y_argmin", "n_support", "n_support_points",
                  "n_excluded", "a", "n_star", "y_star", "margin_pct",
                  "valid", "note"]
    with (OUT / "fit_diagnostics.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fit_fields)
        w.writeheader()
        for r in fit_rows:
            w.writerow({k: ("" if r.get(k) is None else
                            ("%.12g" % r[k] if isinstance(r[k], float) else r[k]))
                        for k in fit_fields})
    cross_fields = ["group", "N", "quantity", "estimator", "n1", "n2",
                    "Re_low", "Re_high", "Re_cross", "ratio_low",
                    "ratio_high", "n_bracket_points"]
    with (OUT / "crossing_diagnostics.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cross_fields)
        w.writeheader()
        for r in cross_rows:
            w.writerow({k: ("" if r.get(k) is None else
                            ("%.12g" % r[k] if isinstance(r[k], float) else r[k]))
                        for k in cross_fields})

    # ---------------- report -------------------------------------------------
    L = ["# Qualification des minima et des seuils (donnees archivees)", "",
         "Recipe: central differences on the gradient-valid fluid mask; "
         "A_mask = n_valid dx^2; D/A_mask uses the SAME support as D. "
         "Estimator: sampled argmin, then an ordinary-least-squares quadratic "
         "on either 3 points (argmin plus one neighbour on each side) or 5 "
         "points (two neighbours on each side). Non-finite values are excluded "
         "before fitting; the fitted vertex is accepted only if a>0 and it "
         "lies inside the support, otherwise argmin is retained and flagged.", ""]
    L += ["## Sensibilite du fit : N=128 union, Re=300/500/1000", "",
          "| Re | quantity | 3-pt n* | 5-pt n* | argmin | margin 3-pt % | margin 5-pt % |",
          "|---:|---|---:|---:|---:|---:|---:|"]
    for Re in (300.0, 500.0, 1000.0):
        for q in QUANTITIES:
            r3 = next(r for r in fit_rows if r["group"] == "N128_union"
                      and r["Re"] == Re and r["quantity"] == q and r["estimator"].startswith("OLS quadratic, 3"))
            r5 = next(r for r in fit_rows if r["group"] == "N128_union"
                      and r["Re"] == Re and r["quantity"] == q and r["estimator"].startswith("OLS quadratic, 5"))
            L.append("| %g | %s | %s | %s | %g | %s | %s |" %
                     (Re, q, "-" if r3["n_star"] is None else "%.3f" % r3["n_star"],
                      "-" if r5["n_star"] is None else "%.3f" % r5["n_star"],
                      r3["n_argmin"],
                      "-" if r3["margin_pct"] is None else "%.3f" % r3["margin_pct"],
                      "-" if r5["margin_pct"] is None else "%.3f" % r5["margin_pct"]))
    L += ["", "## Resolution sensitivity of n*_D (5-point fits where available)", "",
          "| group | Re | n*_D (5-pt) | argmin D | n*_D/A (5-pt) | argmin D/A |",
          "|---|---:|---:|---:|---:|---:|"]
    for label in ("N128_union", "N256_union", "N384_HR", "N512_HR"):
        g = group_data[label]
        for Re in sorted(set(r["Re"] for r in g)):
            if Re not in (100.0, 300.0, 500.0, 1000.0):
                continue
            c = curve(g, Re)
            fD = fit(c, "D", 2)
            fDA = fit(c, "D_over_A_mask", 2)
            L.append("| %s | %g | %s | %g | %s | %g |" %
                     (label, Re,
                      "-" if fD["n_star"] is None else "%.3f" % fD["n_star"],
                      fD["n_argmin"],
                      "-" if fDA["n_star"] is None else "%.3f" % fDA["n_star"],
                      fDA["n_argmin"]))
    L += ["", "## Crossing diagnostics (log-interpolated; descriptive only)", "",
          "| group | quantity | n1/n2 | bracket | Re_c | ratios at bracket |",
          "|---|---|---|---|---:|---|"]
    for r in cross_rows:
        br = ("--" if r["Re_low"] is None else
              "[%g, %g]" % (r["Re_low"], r["Re_high"]))
        rr = ("--" if r["ratio_low"] is None else
              "%.4f -> %.4f" % (r["ratio_low"], r["ratio_high"]))
        L.append("| %s | %s | %g/%g | %s | %s | %s |" %
                 (r["group"], r["quantity"], r["n1"], r["n2"], br,
                  "--" if r["Re_cross"] is None else "%.1f" % r["Re_cross"], rr))
    L += ["", "Interpretation: fitted locations are compared only on matched "
          "grids; absolute D levels are resolution-sensitive. A crossing of "
          "two sampled values is a threshold crossing at the sampling "
          "resolution, not an onset or a resolution-independent threshold.", ""]
    (OUT / "minima_qualification_report.md").write_text("\n".join(L), encoding="utf-8")

    print("cases:", len(all_rows), "fits:", len(fit_rows),
          "crossings:", len(cross_rows))
    print("report ->", OUT / "minima_qualification_report.md")


if __name__ == "__main__":
    main()
