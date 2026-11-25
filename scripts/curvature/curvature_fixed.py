# -*- coding: utf-8 -*-
"""Corrected window-averaged wall-curvature diagnostic for PH13.

WHY THIS FILE EXISTS
--------------------
The production scripts

  08_operator_train/PH13_K5_campaign/PH13_16_make_nearwall_curvature_analysis.py
  06_physics/construire_figure_nearwall.py
  06_physics/etude_convergence_paroi.py

all contain the same defect in ``Boundary.__init__``:

    half = self.n_samples // 2                 # 10000
    s_half, th_half = s_d[:half], theta_d[:half]
    self.theta = np.interp(self.s % (half*self.ds), s_half, th_half)
    self.theta[self.s >= half*self.ds] += pi

``s_d`` has ``n_dense = 200001`` entries over the full perimeter, so
``s_d[:10000]`` covers only 5% of the arclength.  The parameter theta(s) is
therefore compressed into [0, 0.314] (and [pi, pi+0.314]) instead of [0, 2pi),
and the resulting (x, y) samples collapse onto two tiny arcs.  The tangent
angle obtained from ``np.gradient`` of those collapsed samples is numerical
noise, which is why the n=2 unit circle -- whose exact curvature is 1 -- was
reported with kappa_w,max = 29.87 and kappa_w,rms = 4.01.

THE FIX
-------
1. Build theta(s) by direct interpolation of the dense arclength table over
   the FULL perimeter (periodically extended).
2. Compute the tangent angle from periodic central differences, then use a
   WRAPPED angle difference over the physical arclength window w.  This
   removes the spurious 2pi jump at the s=0/P seam.
3. Evaluate the sharp set from the same windowed kappa field at each wall
   point, instead of indexing ``sharp`` by a uniform-grid guess.

Validation: for n=2, a=b=1 the boundary is the unit circle and the corrected
diagnostic must return kappa_w = 1 to sampling accuracy for every window and
every n_samples.

This script is inference-only: it reads the archived LBM fields and writes
corrected tables; it runs no new simulation and trains no model.
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

import numpy as np
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
DATA190 = ROOT / "05_dataset" / "data_all190"
OLD_CSV = ROOT / "06_physics" / "figures_190" / "tables" / "PH13_nearwall_curvature_analysis_190.csv"

WINDOW_OVER_LC = 0.05          # physical arclength window, as in production
SHARP_SET_FACTOR = 2.0         # kappa_w >= 2*<kappa>  (for the circle: no point)
DELTA_OVER_LC = (0.025, 0.05)  # wall bands used in the production analysis


# ---------------------------------------------------------------------------
# geometry
# ---------------------------------------------------------------------------
def superellipse_point(theta, n):
    c, s = np.cos(theta), np.sin(theta)
    return (np.sign(c) * np.abs(c) ** (2.0 / n),
            np.sign(s) * np.abs(s) ** (2.0 / n))


def boundary_theta_from_point(xw, yw, n):
    ct = np.sign(xw) * np.abs(xw) ** (0.5 * n)
    st = np.sign(yw) * np.abs(yw) ** (0.5 * n)
    return np.arctan2(st, ct)


class BoundaryFixed:
    """Uniform-arclength superellipse with a correctly unwrapped tangent angle."""

    def __init__(self, n, n_samples=20000, n_dense=200001):
        self.n = float(n)
        theta_d = np.linspace(0.0, 2.0 * math.pi, n_dense, endpoint=False)
        xd, yd = superellipse_point(theta_d, n)
        seg = np.hypot(np.roll(xd, -1) - xd, np.roll(yd, -1) - yd)
        s_d = np.concatenate(([0.0], np.cumsum(seg[:-1])))
        self.perimeter = float(np.sum(seg))
        self.s_dense, self.theta_dense = s_d, theta_d

        self.n_samples = int(n_samples)
        self.ds = self.perimeter / self.n_samples
        self.s = np.arange(self.n_samples) * self.ds

        # CORRECT theta(s): interpolate over the whole perimeter.
        s_ext = np.concatenate((s_d, [self.perimeter]))
        th_ext = np.concatenate((theta_d, [2.0 * math.pi]))
        self.theta = np.interp(self.s, s_ext, th_ext)

        self.x, self.y = superellipse_point(self.theta, n)
        # Periodic central differences -> no seam artefact.
        dxds = (np.roll(self.x, -1) - np.roll(self.x, 1)) / (2.0 * self.ds)
        dyds = (np.roll(self.y, -1) - np.roll(self.y, 1)) / (2.0 * self.ds)
        phi = np.unwrap(np.arctan2(dyds, dxds))
        # unwrap can leave a 2pi offset between the last and first sample;
        # force a monotone representation on the closed curve.
        if phi[-1] < phi[0]:
            phi[-1] += 2.0 * math.pi
        self.phi = phi
        self.kappa_mean = 2.0 * math.pi / self.perimeter

    def window_curvature(self, window):
        """kappa_w on s_mid, using a wrapped tangent-angle difference."""
        k = max(int(round(0.5 * window / self.ds)), 1)
        dphi = (np.roll(self.phi, -k) - np.roll(self.phi, k) + math.pi) % (2.0 * math.pi) - math.pi
        kappa = dphi / (2.0 * k * self.ds)
        s_mid = (self.s + k * self.ds) % self.perimeter
        return kappa, s_mid

    def kappa_at(self, s_query, kappa, s_mid):
        order = np.argsort(s_mid)
        xs = s_mid[order]
        ys = kappa[order]
        xs_ext = np.concatenate((xs, [xs[0] + self.perimeter]))
        ys_ext = np.concatenate((ys, [ys[0]]))
        return np.interp(np.mod(np.asarray(s_query, float), self.perimeter), xs_ext, ys_ext)

    def theta_to_arclength(self, theta):
        th = np.mod(np.asarray(theta, float), 2.0 * math.pi)
        return np.interp(th, self.theta_dense, self.s_dense, period=2.0 * math.pi)


# ---------------------------------------------------------------------------
# field operators (identical convention to the production analysis)
# ---------------------------------------------------------------------------
def gradient_valid_mask(fluid):
    v = np.zeros_like(fluid, dtype=bool)
    v[1:-1, 1:-1] = (fluid[1:-1, 1:-1] & fluid[:-2, 1:-1] & fluid[2:, 1:-1]
                     & fluid[1:-1, :-2] & fluid[1:-1, 2:])
    return v


def dissipation_density(ux, uy, fluid, re, dx):
    """phi = (1/Re)*2 S:S ; D = 2 * sum(phi) * dx^2 with nu = 2/Re."""
    v = gradient_valid_mask(fluid)
    g = [np.full(ux.shape, np.nan) for _ in range(4)]
    g[0][1:-1, 1:-1] = (ux[1:-1, 2:] - ux[1:-1, :-2]) / (2.0 * dx)
    g[1][1:-1, 1:-1] = (uy[1:-1, 2:] - uy[1:-1, :-2]) / (2.0 * dx)
    g[2][1:-1, 1:-1] = (ux[2:, 1:-1] - ux[:-2, 1:-1]) / (2.0 * dx)
    g[3][1:-1, 1:-1] = (uy[2:, 1:-1] - uy[:-2, 1:-1]) / (2.0 * dx)
    ux_x, uy_x, ux_y, uy_y = g
    phi = (2.0 * ux_x**2 + 2.0 * uy_y**2 + (ux_y + uy_x)**2) / re
    phi = np.where(v, phi, 0.0)
    return phi, v


def analyse(path):
    with np.load(path) as z:
        n, re = float(z["n"]), float(z["Re"])
        ux, uy = np.asarray(z["ux"], float), np.asarray(z["uy"], float)
        fluid = np.asarray(z["fluid"]).astype(bool)
        xx, yy = np.asarray(z["X"], float), np.asarray(z["Y"], float)
        dx = float(abs(xx[0, 1] - xx[0, 0]))
        area_exact = float(z["area_exact"])
        lc = float(z["L_char"]) * dx
        cid = str(z["case_id"])

    phi, valid = dissipation_density(ux, uy, fluid, re, dx)
    cell = dx * dx
    D = 2.0 * float(np.sum(phi)) * cell
    A_mask = float(np.count_nonzero(valid)) * cell

    bc = BoundaryFixed(n)
    window = WINDOW_OVER_LC * lc
    kappa, s_mid = bc.window_curvature(window)
    weights = bc.ds / bc.perimeter
    kmax = float(np.max(kappa))
    krms = float(np.sqrt(np.sum(weights * kappa**2)))
    sharp_frac = float(np.count_nonzero(kappa >= SHARP_SET_FACTOR * bc.kappa_mean) / kappa.size)

    dist_cells, idx = ndimage.distance_transform_edt(fluid, return_indices=True)
    dist = dist_cells * dx
    theta_w = boundary_theta_from_point(xx[idx[0], idx[1]], yy[idx[0], idx[1]], n)
    s_w = bc.theta_to_arclength(theta_w)
    kw = bc.kappa_at(s_w, kappa, s_mid)
    sharp_w = kw >= SHARP_SET_FACTOR * bc.kappa_mean

    kD = float(np.sum(np.where(valid, phi * np.where(np.isnan(kw), 0.0, kw), 0.0)) / np.sum(phi))
    f_sharp = 2.0 * float(np.sum(np.where(sharp_w, phi, 0.0))) * cell / D

    out = dict(case_id=cid, n=n, Re=re, D=D, A_mask=A_mask, D_over_A_mask=D / A_mask,
               area_exact=area_exact,
               kappa_mean=bc.kappa_mean, kappa_w_max=kmax, kappa_w_rms=krms,
               sharp_arclength_fraction=sharp_frac, kappa_D_weighted=kD,
               f_sharp_total=f_sharp)
    for frac in DELTA_OVER_LC:
        band = valid & (dist <= frac * lc)
        out["f_band_%g" % frac] = 2.0 * float(np.sum(np.where(band, phi, 0.0))) * cell / D
    return out


# ---------------------------------------------------------------------------
# checks
# ---------------------------------------------------------------------------
def circle_test():
    print("=== analytical circle test (n=2, a=b=1, kappa_exact = 1) ===")
    print(" n_samples   window/Lc   kappa_max    kappa_rms   arclength_mean   f_sharp")
    rows = []
    for ns in (2000, 5000, 20000, 50000):
        for wfrac in (0.01, 0.05, 0.10):
            bc = BoundaryFixed(2.0, n_samples=ns)
            k, sm = bc.window_curvature(wfrac * bc.perimeter / 2.0)  # Lc = 2
            rows.append(dict(n_samples=ns, window_over_Lc=wfrac,
                             kmax=float(k.max()), krms=float(np.sqrt(np.sum(bc.ds / bc.perimeter * k**2))),
                             kmean_exact=bc.kappa_mean, f_sharp=float(np.mean(k >= 2 * bc.kappa_mean))))
            print("  %7d     %5.2f      %9.6f   %9.6f     %9.6f      %.3f"
                  % (ns, wfrac, rows[-1]["kmax"], rows[-1]["krms"],
                     rows[-1]["kmean_exact"], rows[-1]["f_sharp"]))
    ok = all(abs(r["kmax"] - 1.0) < 2e-2 and abs(r["krms"] - 1.0) < 2e-2 for r in rows)
    print("  PASS" if ok else "  FAIL")
    return ok


def main():
    if not circle_test():
        raise SystemExit("curvature fix rejected: unit-circle test failed")

    old = {}
    with OLD_CSV.open(newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            old[r["case_id"]] = r

    rows = []
    for p in sorted(DATA190.glob("*.npz")):
        rows.append(analyse(p))
        if len(rows) % 40 == 0:
            print("  recomputed", len(rows), "cases")

    fields = ("case_id", "n", "Re", "D", "A_mask", "D_over_A_mask", "area_exact",
              "kappa_mean", "kappa_w_max", "kappa_w_rms", "sharp_arclength_fraction",
              "kappa_D_weighted", "f_sharp_total", "f_band_0.025", "f_band_0.05")
    with (OUT / "curvature_corrected_190.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in fields})

    with (OUT / "curvature_before_after.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["case_id", "n", "Re",
                    "old_kappa_w_max", "new_kappa_w_max",
                    "old_kappa_w_rms", "new_kappa_w_rms",
                    "old_f_sharp", "new_f_sharp",
                    "old_kappa_D_weighted", "new_kappa_D_weighted"])
        for r in rows:
            o = old.get(r["case_id"], {})
            w.writerow([r["case_id"], r["n"], r["Re"],
                        o.get("kappa_w_max", ""), r["kappa_w_max"],
                        o.get("kappa_w_rms", ""), r["kappa_w_rms"],
                        o.get("sharp_arclength_fraction", ""), r["sharp_arclength_fraction"],
                        o.get("kappa_D_weighted", ""), r["kappa_D_weighted"]])

    print("\n=== n=2 cases, before -> after ===")
    for r in rows:
        if abs(r["n"] - 2.0) < 1e-9:
            print("  Re=%6.0f  kmax %.3f -> %.5f   krms %.3f -> %.5f   fsharp %.4f -> %.4f"
                  % (r["Re"], float(old[r["case_id"]]["kappa_w_max"]), r["kappa_w_max"],
                     float(old[r["case_id"]]["kappa_w_rms"]), r["kappa_w_rms"],
                     float(old[r["case_id"]]["sharp_arclength_fraction"]), r["sharp_arclength_fraction"]))
    print("\nwrote", OUT / "curvature_corrected_190.csv")


if __name__ == "__main__":
    main()
