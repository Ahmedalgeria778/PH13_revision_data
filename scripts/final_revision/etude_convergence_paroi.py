# -*- coding: utf-8 -*-
"""
06_physics/etude_convergence_paroi.py

Etude de convergence spatiale des diagnostics proche paroi (chantier B).

Replique a l'identique l'algorithme canonique
PH13_16_make_nearwall_curvature_analysis.py (parametrisation en arclength de la
frontiere, masque gradient-valide a cinq points, integrale de taux de
deformation, bandes Omega_delta, ensemble "aigu", moyennes ponderees par la
dissipation) sur trois resolutions N = 64, 128, 256, pour trois cas
representatifs :

    (n=1.25, Re=300)  pointee, bas Re
    (n=3.0,  Re=1000) minimum D/A a haut Re (anchor)
    (n=8.0,  Re=1000) pres-carree, OOD (courbure frontiere maximale)

N=128 est relu depuis 05_dataset/data_all190 (grille physique) ; N=64 et
N=256 sont produits par 05_dataset/generate_convergence.py (data_conv/).

Pour chaque diagnostic d, la convergence est resumee par :
  - les valeurs aux trois N ;
  - les variations relatives |q(N2)-q(N1)|/|q(N2)| ;
  - l'ordre empirique p = log2( |q64-q128| / |q128-q256| ) (Richardson, r=2) ;
  - la valeur extrapolee q_inf = q256 + (q256-q128)/(2^p - 1) quand p > 0 ;
  - le critere de plateau (variation < 1 % entre 128 et 256).

Sorties : 06_physics/results_convergence/{csv, md, png}. Aucune simulation.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np
from scipy import ndimage  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ALL190 = ROOT / "05_dataset" / "data_all190"
CONV = ROOT / "05_dataset" / "data_conv"
OUT_DIR = ROOT / "06_physics" / "results_convergence"

CASES = ((1.25, 300.0), (3.0, 1000.0), (8.0, 1000.0))
NS = (64, 128, 256)

DELTA_OVER_LC = (0.025, 0.05)
WINDOW_OVER_LC = 0.05
SHARP_SET_FACTOR = 2.0

# diagnostics suivis (convergence + ordre)
DIAGS = ("D_A", "f_delta_025", "f_delta_05", "f_sharp_total",
         "kappa_D_weighted", "umax")


# ------------------------------------------------------------------ geometry
def superellipse_point(theta, n):
    c = np.cos(theta)
    s = np.sin(theta)
    x = np.sign(c) * np.abs(c) ** (2.0 / n)
    y = np.sign(s) * np.abs(s) ** (2.0 / n)
    return x, y


def boundary_theta_from_point(xw, yw, n):
    ct = np.sign(xw) * np.abs(xw) ** (0.5 * n)
    st = np.sign(yw) * np.abs(yw) ** (0.5 * n)
    return np.arctan2(st, ct)


class Boundary:
    """Uniform-arclength representation of the closed superellipse boundary."""

    def __init__(self, n, n_samples=20000, n_dense=200001):
        self.n = float(n)
        theta_d = np.linspace(0.0, 2.0 * math.pi, n_dense, endpoint=False)
        xd, yd = superellipse_point(theta_d, n)
        seg = np.hypot(np.roll(xd, -1) - xd, np.roll(yd, -1) - yd)
        s_d = np.concatenate(([0.0], np.cumsum(seg[:-1])))
        self.perimeter = float(np.sum(seg))
        self.s_dense = s_d
        self.theta_dense = theta_d
        self.n_samples = int(n_samples)
        self.ds = self.perimeter / self.n_samples
        self.s = np.arange(self.n_samples) * self.ds
        half = self.n_samples // 2
        s_half, th_half = s_d[:half], theta_d[:half]
        self.theta = np.interp(self.s % (half * self.ds), s_half, th_half)
        self.theta[self.s >= half * self.ds] += math.pi
        self.x, self.y = superellipse_point(self.theta, n)
        self.phi = np.unwrap(np.arctan2(np.gradient(self.y, self.ds),
                                        np.gradient(self.x, self.ds)))
        self.kappa_mean = 2.0 * math.pi / self.perimeter

    def window_curvature(self, window):
        k = max(int(round(0.5 * window / self.ds)), 1)
        dphi = np.abs(np.roll(self.phi, -k) - np.roll(self.phi, k))
        kappa = dphi / (2.0 * k * self.ds)
        s_mid = (self.s + k * self.ds) % self.perimeter
        return kappa, s_mid

    def curvature_at_arclength(self, s_query, kappa, s_mid):
        order = np.argsort(s_mid)
        s_sorted = s_mid[order]
        k_sorted = kappa[order]
        s_ext = np.concatenate((s_sorted, [s_sorted[0] + self.perimeter]))
        k_ext = np.concatenate((k_sorted, [k_sorted[0]]))
        return np.interp(np.mod(np.asarray(s_query, dtype=float), self.perimeter),
                         s_ext, k_ext)

    def theta_to_arclength(self, theta):
        return np.interp(np.mod(np.asarray(theta, dtype=float), 2.0 * math.pi),
                         self.theta_dense, self.s_dense, period=2.0 * math.pi)


# ---------------------------------------------------------------- diagnostics
def gradient_valid_mask(fluid):
    interior = np.zeros_like(fluid, dtype=bool)
    interior[1:-1, 1:-1] = (
        fluid[1:-1, 1:-1] & fluid[:-2, 1:-1] & fluid[2:, 1:-1]
        & fluid[1:-1, :-2] & fluid[1:-1, 2:]
    )
    return interior


def find_file(n, Re, N):
    cid = f"se_n{str(round(n, 2)).replace('.', 'p')}_Re{int(round(Re))}_N{N}"
    for d in (CONV, ALL190):
        p = d / f"{cid}.npz"
        if p.exists():
            return p
    return None


def analyse_case(path: Path, boundary: Boundary) -> dict:
    with np.load(path) as data:
        n = float(data["n"])
        re = float(data["Re"])
        N = int(data["N"])
        ux = np.asarray(data["ux"], dtype=float)
        uy = np.asarray(data["uy"], dtype=float)
        fluid = np.asarray(data["fluid"]).astype(bool)
        xx = np.asarray(data["X"], dtype=float)
        yy = np.asarray(data["Y"], dtype=float)
        area = float(data["area_exact"])
        L_char = float(data["L_char"])
        case_id = str(data["case_id"])
    dx = float(abs(xx[0, 1] - xx[0, 0]))
    l_c = L_char * dx
    valid = gradient_valid_mask(fluid)

    ux_x = np.full(ux.shape, np.nan)
    uy_x = np.full(ux.shape, np.nan)
    ux_y = np.full(ux.shape, np.nan)
    uy_y = np.full(ux.shape, np.nan)
    ux_x[1:-1, 1:-1] = (ux[1:-1, 2:] - ux[1:-1, :-2]) / (2.0 * dx)
    uy_x[1:-1, 1:-1] = (uy[1:-1, 2:] - uy[1:-1, :-2]) / (2.0 * dx)
    ux_y[1:-1, 1:-1] = (ux[2:, 1:-1] - ux[:-2, 1:-1]) / (2.0 * dx)
    uy_y[1:-1, 1:-1] = (uy[2:, 1:-1] - uy[:-2, 1:-1]) / (2.0 * dx)
    for arr in (ux_x, uy_x, ux_y, uy_y):
        arr[~valid] = np.nan

    phi = (2.0 * ux_x ** 2 + 2.0 * uy_y ** 2 + (ux_y + uy_x) ** 2) / re
    phi = np.where(valid, phi, 0.0)
    cell = dx * dx
    strain_integral = float(np.sum(phi) * cell)
    dissipation = 2.0 * strain_integral

    umax = float(np.hypot(ux[fluid], uy[fluid]).max())

    kappa, s_mid = boundary.window_curvature(WINDOW_OVER_LC * l_c)
    sharp = kappa >= SHARP_SET_FACTOR * boundary.kappa_mean

    dist_cells, indices = ndimage.distance_transform_edt(fluid,
                                                         return_indices=True)
    dist = dist_cells * dx
    theta_w = boundary_theta_from_point(xx[indices[0], indices[1]],
                                        yy[indices[0], indices[1]], n)
    s_w = boundary.theta_to_arclength(theta_w)
    kappa_field = boundary.curvature_at_arclength(s_w, kappa, s_mid)
    kappa_field = np.where(valid, kappa_field, np.nan)
    sharp_field = np.where(valid, sharp[np.clip(
        np.searchsorted(boundary.s, np.mod(s_w, boundary.perimeter)), 0,
        boundary.n_samples - 1)], False)

    out = {"case_id": case_id, "n": n, "Re": re, "N": N,
           "A": area, "L_c": l_c, "D": dissipation,
           "D_A": dissipation / area, "umax": umax,
           "perimeter": boundary.perimeter, "kappa_mean": boundary.kappa_mean}
    total_phi = float(np.sum(phi))
    out["kappa_D_weighted"] = float(np.sum(
        np.where(valid, phi * np.nan_to_num(kappa_field), 0.0)) / total_phi)
    out["f_sharp_total"] = float(
        2.0 * np.sum(np.where(sharp_field, phi, 0.0)) * cell) / dissipation
    for frac in DELTA_OVER_LC:
        delta = frac * l_c
        band = valid & (dist <= delta)
        key = f"{frac:g}".replace("0.", "")
        phi_band = float(np.sum(np.where(band, phi, 0.0)))
        d_band = 2.0 * phi_band * cell
        out[f"delta_over_Lc_{key}"] = frac
        out[f"D_delta_{key}"] = d_band
        out[f"f_delta_{key}"] = d_band / dissipation
        out[f"band_cells_{key}"] = float(np.count_nonzero(band))
        out[f"kappa_D_weighted_delta_{key}"] = (
            float(np.sum(np.where(band, phi * np.nan_to_num(kappa_field), 0.0))
                  / phi_band) if phi_band > 0 else float("nan"))
        out[f"f_sharp_delta_{key}"] = float(
            2.0 * np.sum(np.where(band & sharp_field, phi, 0.0)) * cell
        ) / dissipation
    out["dist_max"] = float(np.max(dist[valid]))
    return out


# ------------------------------------------------------------------ robustesse
def richardson(q: dict[int, float], name: str) -> dict:
    """Ordre empirique p et extrapolation de Richardson sur N = 64, 128, 256."""
    out = {"name": name, "values": {N_: None for N_ in NS}}
    for N_ in NS:
        out["values"][N_] = q.get(N_)
    v64, v128, v256 = (q.get(64), q.get(128), q.get(256))
    if not all(v is not None and math.isfinite(v) and abs(v) > 1e-300
               for v in (v64, v128, v256)):
        out["change_64_128"] = None
        out["change_128_256"] = None
        out["order_p"] = None
        out["q_extrap"] = None
        out["plateau_1pct"] = None
        return out
    e12 = abs(v128 - v64)
    e23 = abs(v256 - v128)
    out["change_64_128"] = e12 / abs(v128) if v128 else None
    out["change_128_256"] = e23 / abs(v256) if v256 else None
    out["plateau_1pct"] = bool(out["change_128_256"] is not None
                               and out["change_128_256"] < 0.01)
    if e12 > 0 and e23 > 0 and e23 < e12:
        p = math.log2(e12 / e23)
        out["order_p"] = p
        out["q_extrap"] = v256 + (v256 - v128) / (2.0 ** p - 1.0) if p > 0 else None
    else:
        out["order_p"] = None
        out["q_extrap"] = None
    return out


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for n, Re in CASES:
        boundary = Boundary(n)
        for N in NS:
            p = find_file(n, Re, N)
            if p is None:
                continue
            row = analyse_case(p, boundary)
            row["source"] = str(p.relative_to(ROOT))
            rows.append(row)
            print(f"[conv-paroi] {row['case_id']} OK (N={N})", flush=True)

    # convergence par cas x diagnostic
    cases_rows: dict[tuple, dict[int, dict]] = {}
    for row in rows:
        cases_rows.setdefault((row["n"], row["Re"]), {})[row["N"]] = row
    per_case_diag = {}
    for (n, Re), byN in cases_rows.items():
        q = {d: {} for d in DIAGS}
        for N, row in byN.items():
            for d in DIAGS:
                q[d][N] = row[d]
        per_case_diag[(n, Re)] = {d: richardson(q[d], d) for d in DIAGS}

    with (OUT_DIR / "convergence_paroi.csv").open("w", newline="",
                                                  encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["case_id", "n", "Re", "N", "D_A", "f_delta_025",
                    "f_delta_05", "f_sharp_total", "kappa_D_weighted", "umax"])
        for row in sorted(rows, key=lambda r: (r["n"], r["Re"], r["N"])):
            w.writerow([row["case_id"], row["n"], row["Re"], row["N"],
                        f"{row['D_A']:.6e}", f"{row['f_delta_025']:.6f}",
                        f"{row['f_delta_05']:.6f}", f"{row['f_sharp_total']:.6f}",
                        f"{row['kappa_D_weighted']:.6f}", f"{row['umax']:.6f}"])

    lines = ["# Convergence spatiale des diagnostics proche paroi (chantier B)",
             "",
             "Replique de l'algorithme canonique PH13_16 sur N=64/128/256.",
             "",
             "| cas | N | D/A | f_delta_0.025 | f_delta_0.05 | f_sharp | "
             "kappa_D_w | umax |",
             "|---|---|---|---|---|---|---|---|"]
    for row in sorted(rows, key=lambda r: (r["n"], r["Re"], r["N"])):
        lines.append(f"| {row['case_id']} | {row['N']} | {row['D_A']:.4e} | "
                     f"{row['f_delta_025']:.4f} | {row['f_delta_05']:.4f} | "
                     f"{row['f_sharp_total']:.4f} | {row['kappa_D_weighted']:.4f} "
                     f"| {row['umax']:.4f} |")
    lines += ["", "## Ordre empirique (Richardson, r=2) et extrapolation", ""]
    lines.append("| cas | diag | p | q_extrap | var128-256 | plateau<1% |")
    lines.append("|---|---|---|---|---|---|")
    for (n, Re), diags in per_case_diag.items():
        for d in DIAGS:
            r = diags[d]
            p_ = "%.2f" % r["order_p"] if r["order_p"] else "-"
            ext = "%.4e" % r["q_extrap"] if r["q_extrap"] is not None else "-"
            ch = "%.3f" % r["change_128_256"] if r["change_128_256"] is not None else "-"
            pl = "oui" if r["plateau_1pct"] else "non"
            lines.append(f"| n={n} Re={Re:g} | {d} | {p_} | {ext} | {ch} | {pl} |")
    (OUT_DIR / "convergence_paroi.md").write_text("\n".join(lines), encoding="utf-8")

    # figure : log10(q) vs log10(N) pour 3 diagnostics sur les 3 cas
    fig, axes = plt.subplots(1, 3, figsize=(13.6, 4.2), constrained_layout=True)
    markers = {1.25: "o", 3.0: "s", 8.0: "^"}
    for ax, diag in zip(axes, ("D_A", "f_delta_025", "f_delta_05")):
        for n, Re in CASES:
            vals = {N: cases_rows[(n, Re)][N][diag] for N in NS
                    if N in cases_rows[(n, Re)]}
            ax.loglog(list(vals.keys()), list(vals.values()),
                      marker=markers[n], label=f"n={n}, Re={Re:g}", lw=1.6)
        ax.set_title(diag)
        ax.set_xlabel("N")
        ax.grid(which="both", alpha=0.3)
    axes[0].legend(fontsize=8)
    fig.savefig(OUT_DIR / "convergence_paroi.png", dpi=200)
    print(f"[conv-paroi] ecrit dans {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())