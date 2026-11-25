# -*- coding: utf-8 -*-
"""Exact FEM dissipation and gradient validation for PH13.

This script answers referee #4.3 / #3.3 with quantities that cannot be
obtained from the archived fields alone:

  * exact Taylor-Hood dissipation  D_FEM = 2*nu*int_Omega S(u):S(u) dA,
    assembled with the same P2 velocity basis used for the solve;
  * mesh sensitivity of D_FEM on nrefs = 4, 5, 6 (reported as differences,
    NOT as a Richardson estimate);
  * exact shape-function gradients at the archived lattice points, compared
    with central differences reconstructed from the SAVED fem_ux/fem_uy.

The last point is explicitly a reconstruction test: the archived fields are
lattice samples of a previous FEM solution, not the FEM DOF vector.  Therefore
the finite-difference gradient is labelled FD(sampled FEM), and the exact FEM
gradient is evaluated by the shape functions of a freshly solved P2 field.

Run with the base interpreter (project venv has no scikit-fem):
    C:/Users/user/AppData/Local/Programs/Python/Python314/python.exe fem_dissipation_validation.py
"""
from __future__ import annotations

import csv
import glob
import math
import os
import sys
import time
from pathlib import Path

import numpy as np
from skfem import Basis, BilinearForm, ElementTriP2, asm
from skfem.helpers import grad

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
for _p in (ROOT / "01_geometry", ROOT / "04_reference_FEM" / "mesh",
           ROOT / "04_reference_FEM" / "solver"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from superellipse import Superellipse  # noqa: E402
from navier_stokes_th import solve_cavity  # noqa: E402

DATA190 = ROOT / "05_dataset" / "data_all190"
N_GRID = (1.25, 2.0, 4.0, 8.0)
RE_GRID = (100.0, 400.0, 1000.0)
NREFS_LADDER = (4, 5, 6)
U_LID = 0.05


@BilinearForm
def symgrad_energy(u, v, w):
    """2*nu * int S(u):S(v), with S = (grad u + grad u^T)/2."""
    gu, gv = grad(u), grad(v)
    s = 0.0
    for i in range(2):
        for j in range(2):
            su = 0.5 * (gu[i, j] + gu[j, i])
            sv = 0.5 * (gv[i, j] + gv[j, i])
            s += su * sv
    return 2.0 * w["nu"] * s


def exact_dissipation(res):
    """Integrated D_FEM = 2*nu*int S:S from the P2 DOF vector."""
    M = asm(symgrad_energy, res.basis["u"], nu=res.nu)
    return float(res.u @ M @ res.u)


def exact_grad_at(res, pts, chunk=192):
    """Exact P2 gradient at arbitrary points; shape (2,2,npoints).

    out[c, j, k] = d u_c / d x_j at point k.  Points outside the mesh are NaN.
    """
    pts = np.asarray(pts, dtype=float)
    bu = res.basis["u"]
    mesh = res.mesh
    bs = Basis(mesh, ElementTriP2(), intorder=4)
    ncomp, npts = 2, pts.shape[1]
    out = np.full((ncomp, 2, npts), np.nan)
    finder = mesh.element_finder(mapping=bs.mapping)
    for s in range(0, npts, chunk):
        x = pts[:, s:s + chunk]
        cells = finder(x[0], x[1])
        ok = cells >= 0
        if not ok.any():
            continue
        idx = np.flatnonzero(ok)
        local = bs.mapping.invF(x[:, ok][:, :, None], tind=cells[ok])
        block = np.zeros((ncomp, 2, idx.size))
        for k in range(bs.Nbfun):
            df = bs.elem.gbasis(bs.mapping, local, k, tind=cells[ok])[0]
            g = df.grad[:, :, 0]           # (2, npoints)
            for c in range(ncomp):
                gdofs = bu.element_dofs[2 * k + c, cells[ok]]
                vals = res.u[gdofs]
                block[c, 0, :] += vals * g[0]
                block[c, 1, :] += vals * g[1]
        out[:, :, s + idx] = block
    return out


def gradient_valid_mask(fluid):
    v = np.zeros_like(fluid, dtype=bool)
    v[1:-1, 1:-1] = (fluid[1:-1, 1:-1] & fluid[:-2, 1:-1] & fluid[2:, 1:-1]
                     & fluid[1:-1, :-2] & fluid[1:-1, 2:])
    return v


def fd_grad(ux, uy, fluid, dx):
    """Central-difference gradient on the production gradient-valid mask."""
    valid = gradient_valid_mask(fluid)
    g = np.full((2, 2) + ux.shape, np.nan)
    g[0, 0][1:-1, 1:-1] = (ux[1:-1, 2:] - ux[1:-1, :-2]) / (2 * dx)
    g[0, 1][1:-1, 1:-1] = (ux[2:, 1:-1] - ux[:-2, 1:-1]) / (2 * dx)
    g[1, 0][1:-1, 1:-1] = (uy[1:-1, 2:] - uy[1:-1, :-2]) / (2 * dx)
    g[1, 1][1:-1, 1:-1] = (uy[2:, 1:-1] - uy[:-2, 1:-1]) / (2 * dx)
    return g, valid


def phi_from_grad(g, re):
    return (2.0 * g[0, 0] ** 2 + 2.0 * g[1, 1] ** 2
            + (g[0, 1] + g[1, 0]) ** 2) / re


def strain(g):
    s = np.empty_like(g)
    s[0, 0] = g[0, 0]
    s[1, 1] = g[1, 1]
    s[0, 1] = s[1, 0] = 0.5 * (g[0, 1] + g[1, 0])
    return s


def archived_path(n, re):
    matches = []
    for p in DATA190.glob("*.npz"):
        with np.load(p) as z:
            if ("N" in z.files and int(z["N"]) == 128
                    and abs(float(z["n"]) - n) < 1e-9
                    and abs(float(z["Re"]) - re) < 1e-9
                    and "fem_ux" in z.files):
                matches.append(p)
    return matches[0] if matches else None


def reconstruct_from_archive(n, re, res_exact):
    path = archived_path(n, re)
    if path is None:
        return None
    with np.load(path) as z:
        ux = np.asarray(z["fem_ux"], float)
        uy = np.asarray(z["fem_uy"], float)
        fluid = np.asarray(z["fluid"]).astype(bool)
        X = np.asarray(z["X"], float)
        Y = np.asarray(z["Y"], float)
        dx = float(abs(X[0, 1] - X[0, 0]))
        archived_nrefs = int(z["fem_nrefs"]) if "fem_nrefs" in z.files else -1
    gf, valid = fd_grad(ux, uy, fluid, dx)
    yy, xx = np.nonzero(valid)
    pts = np.vstack([X[yy, xx], Y[yy, xx]])
    ge = exact_grad_at(res_exact, pts)
    covered = np.isfinite(ge[0, 0])
    re_f = float(re)
    phi_fd_full = phi_from_grad(gf, re_f)
    D_fd = 2.0 * float(np.sum(np.where(valid, phi_fd_full, 0.0))) * dx * dx
    yy, xx = yy[covered], xx[covered]
    ge = ge[:, :, covered]
    gf = gf[:, :, yy, xx]
    cell = dx * dx

    def rel_err(a, b):
        num = float(np.sum((a - b) ** 2))
        den = float(np.sum(b ** 2)) + 1e-30
        return math.sqrt(num / den)

    pe = phi_from_grad(ge, re_f)
    pf = phi_from_grad(gf, re_f)
    D_exact_on_lattice = 2.0 * float(np.sum(pe)) * cell
    se, sf = strain(ge), strain(gf)
    return dict(n=n, Re=re_f, N=128, archived_nrefs=archived_nrefs,
                n_points=int(covered.sum()),
                eps_grad=rel_err(gf, ge), eps_strain=rel_err(sf, se),
                eps_phi=rel_err(pf, pe),
                rms_grad_exact=math.sqrt(float(np.mean(ge ** 2))),
                rms_strain_exact=math.sqrt(float(np.mean(se ** 2))),
                D_FD_lattice=D_fd, D_exact_on_lattice=D_exact_on_lattice,
                rel_D_lattice_error=abs(D_fd - D_exact_on_lattice) / (D_exact_on_lattice + 1e-30),
                source=path.name)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ladder_path = OUT / "fem_dissipation.csv"
    ref_path = OUT / "fem_mesh_refinement.csv"
    recon_path = OUT / "fem_gradient_reconstruction.csv"
    with ladder_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["n", "Re", "nrefs", "iters", "converged", "nnodes", "ntri",
                    "D_FEM_exact", "umax", "wall_s"])
    with ref_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["n", "Re", "nrefs_coarse", "nrefs_fine", "D_coarse",
                    "D_fine", "rel_change"])
    with recon_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["n", "Re", "N", "archived_nrefs", "n_points", "eps_grad",
                    "eps_strain", "eps_phi", "rms_grad_exact", "rms_strain_exact",
                    "D_FD_lattice", "D_exact_on_lattice",
                    "rel_D_lattice_error", "source"])

    D_table = {}
    for n in N_GRID:
        for re in RE_GRID:
            geom = Superellipse(n=n)
            for nrefs in NREFS_LADDER:
                t0 = time.time()
                res = solve_cavity(geom, Re=re, nrefs=nrefs, U_lid=1.0,
                                   lid_mode="upper", verbose=False)
                D = exact_dissipation(res)
                D_table[(n, re, nrefs)] = D
                with ladder_path.open("a", newline="", encoding="utf-8") as fh:
                    csv.writer(fh).writerow([n, re, nrefs, res.iters,
                                             int(res.converged),
                                             res.mesh.p.shape[1], res.mesh.t.shape[1],
                                             "%.12g" % D, "%.10g" % res.umax,
                                             "%.3f" % (time.time() - t0)])
                print("D n=%.2f Re=%.0f nrefs=%d : %.8f (%.1fs)" %
                      (n, re, nrefs, D, time.time() - t0), flush=True)
                if nrefs == NREFS_LADDER[-1]:
                    rec = reconstruct_from_archive(n, re, res)
                    if rec is not None:
                        with recon_path.open("a", newline="", encoding="utf-8") as fh:
                            csv.writer(fh).writerow([
                                rec["n"], rec["Re"], rec["N"], rec["archived_nrefs"],
                                rec["n_points"], "%.10g" % rec["eps_grad"],
                                "%.10g" % rec["eps_strain"], "%.10g" % rec["eps_phi"],
                                "%.10g" % rec["rms_grad_exact"],
                                "%.10g" % rec["rms_strain_exact"],
                                "%.12g" % rec["D_FD_lattice"],
                                "%.12g" % rec["D_exact_on_lattice"],
                                "%.10g" % rec["rel_D_lattice_error"], rec["source"]])
                        print("  reconstruction eps_grad=%.4f eps_phi=%.4f "
                              "relD=%.4f" % (rec["eps_grad"], rec["eps_phi"],
                                             rec["rel_D_lattice_error"]), flush=True)
            for lo, hi in zip(NREFS_LADDER[:-1], NREFS_LADDER[1:]):
                a, b = D_table[(n, re, lo)], D_table[(n, re, hi)]
                with ref_path.open("a", newline="", encoding="utf-8") as fh:
                    csv.writer(fh).writerow([n, re, lo, hi, "%.12g" % a,
                                             "%.12g" % b, "%.10g" % (abs(b - a) / b)])
    print("DONE ->", OUT, flush=True)


if __name__ == "__main__":
    main()
