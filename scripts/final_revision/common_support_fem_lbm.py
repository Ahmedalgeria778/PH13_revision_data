# -*- coding: utf-8 -*-
"""Common-support LBM/FEM dissipation for PH13.

The LBM observable is
    D_LBM^M = 2 nu sum_{M} S_FD:S_FD dx^2,  nu = 2/Re,
evaluated on the production gradient-valid mask M.  The FEM observable on the
same support is obtained by projecting each LBM masked lattice point onto the
Taylor-Hood mesh and evaluating the P2 strain by shape functions:
    D_FEM^M ~= 2 nu sum_{M intersect mesh} S_P2(x_k):S_P2(x_k) dx^2.
The global FEM value D_FEM^Omega is taken from the executed P2/P1 ladder.

Run with:
  C:/Users/user/AppData/Local/Programs/Python/Python314/python.exe common_support_fem_lbm.py
"""
from __future__ import annotations

import csv
import math
import sys
import time
from pathlib import Path

import numpy as np
from skfem import Basis, ElementTriP2

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
for p in (ROOT / "01_geometry", ROOT / "04_reference_FEM" / "mesh",
          ROOT / "04_reference_FEM" / "solver"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
from superellipse import Superellipse  # noqa: E402
from navier_stokes_th import solve_cavity  # noqa: E402

DATA190 = ROOT / "05_dataset" / "data_all190"
FEM_CSV = ROOT / "corrections for reviewer" / "03_FEM_dissipation_validation" / "fem_dissipation.csv"
N_GRID = (1.25, 2.0, 4.0, 8.0)
RE_GRID = (100.0, 1000.0)
NREF = 6


def gradient_valid_mask(fluid):
    v = np.zeros_like(fluid, dtype=bool)
    v[1:-1, 1:-1] = (fluid[1:-1, 1:-1] & fluid[:-2, 1:-1] & fluid[2:, 1:-1]
                     & fluid[1:-1, :-2] & fluid[1:-1, 2:])
    return v


def fd_grad(ux, uy, dx):
    g = np.full((2, 2) + ux.shape, np.nan)
    g[0, 0][1:-1, 1:-1] = (ux[1:-1, 2:] - ux[1:-1, :-2]) / (2 * dx)
    g[0, 1][1:-1, 1:-1] = (ux[2:, 1:-1] - ux[:-2, 1:-1]) / (2 * dx)
    g[1, 0][1:-1, 1:-1] = (uy[1:-1, 2:] - uy[1:-1, :-2]) / (2 * dx)
    g[1, 1][1:-1, 1:-1] = (uy[2:, 1:-1] - uy[:-2, 1:-1]) / (2 * dx)
    return g


def strain_from_grad(g):
    s = np.empty_like(g)
    s[0, 0] = g[0, 0]
    s[1, 1] = g[1, 1]
    s[0, 1] = s[1, 0] = 0.5 * (g[0, 1] + g[1, 0])
    return s


def sss(s):
    return s[0, 0]**2 + s[1, 1]**2 + 2.0 * s[0, 1]**2


def fem_grad_at(res, pts, chunk=256):
    """P2 velocity gradient at points; out[c,j,k] = d u_c / dx_j."""
    pts = np.asarray(pts, dtype=float)
    bu = res.basis["u"]
    bs = Basis(res.mesh, ElementTriP2(), intorder=4)
    finder = res.mesh.element_finder(mapping=bs.mapping)
    out = np.full((2, 2, pts.shape[1]), np.nan)
    cells_all = np.full(pts.shape[1], -1, dtype=np.int64)
    for s in range(0, pts.shape[1], chunk):
        x = pts[:, s:s + chunk]
        cells = finder(x[0], x[1])
        cells_all[s:s + chunk] = cells
        ok = cells >= 0
        if not np.any(ok):
            continue
        idx = np.flatnonzero(ok)
        local = bs.mapping.invF(x[:, ok][:, :, None], tind=cells[ok])
        block = np.zeros((2, 2, idx.size))
        for k in range(bs.Nbfun):
            df = bs.elem.gbasis(bs.mapping, local, k, tind=cells[ok])[0]
            g = df.grad[:, :, 0]
            for c in range(2):
                gdofs = bu.element_dofs[2 * k + c, cells[ok]]
                vals = res.u[gdofs]
                block[c, 0, :] += vals * g[0]
                block[c, 1, :] += vals * g[1]
        out[:, :, s + idx] = block
    return out, cells_all


def archived_path(n, re):
    for p in sorted(DATA190.glob('se_n*_Re*.npz')):
        with np.load(p) as z:
            if (int(z['N']) == 128 and abs(float(z['n']) - n) < 1e-9
                    and abs(float(z['Re']) - re) < 1e-9 and 'fem_ux' in z.files):
                return p
    raise FileNotFoundError((n, re))


def read_fem_global():
    table = {}
    with FEM_CSV.open(newline='', encoding='utf-8') as fh:
        for row in csv.DictReader(fh):
            if int(row['nrefs']) == NREF:
                table[(float(row['n']), float(row['Re']))] = float(row['D_FEM_exact'])
    return table


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    fem_global = read_fem_global()
    out_path = OUT / 'common_support_dissipation.csv'
    with out_path.open('w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(['n', 'Re', 'N', 'nrefs', 'nu', 'n_mask_lbm', 'n_covered_fem',
                    'D_LBM_M', 'D_FEM_M', 'D_FEM_Omega', 'eps_D_percent',
                    'D_FEM_Omega_over_FEM_M', 'source_lbm'])
        for n in N_GRID:
            for re in RE_GRID:
                t0 = time.time()
                path = archived_path(n, re)
                with np.load(path) as z:
                    ux = np.asarray(z['ux'], dtype=float)
                    uy = np.asarray(z['uy'], dtype=float)
                    fluid = np.asarray(z['fluid'], dtype=bool)
                    X = np.asarray(z['X'], dtype=float)
                    Y = np.asarray(z['Y'], dtype=float)
                    dx = abs(float(X[0, 1] - X[0, 0]))
                    u_lid = float(z['U_lid'])
                    nu_lbm = float(z['nu_lbm'])
                mask = gradient_valid_mask(fluid)
                yy, xx = np.nonzero(mask)
                pts = np.vstack([X[yy, xx], Y[yy, xx]])
                gf = fd_grad(ux, uy, dx)
                sf = strain_from_grad(gf[:, :, yy, xx])
                nu = 2.0 / re
                D_lbm = 2.0 * nu * float(np.sum(sss(sf))) * dx * dx

                geom = Superellipse(n=n)
                res = solve_cavity(geom, Re=re, nrefs=NREF, U_lid=1.0,
                                   lid_mode='upper', verbose=False)
                ge, cells = fem_grad_at(res, pts)
                covered = cells >= 0
                se = strain_from_grad(ge[:, :, covered])
                D_fem_m = 2.0 * nu * float(np.sum(sss(se))) * dx * dx
                D_fem_omega = fem_global[(n, re)]
                eps = 100.0 * abs(D_lbm - D_fem_m) / D_fem_m
                w.writerow([
                    n, re, 128, NREF, '%.12g' % nu, len(yy), int(covered.sum()),
                    '%.12g' % D_lbm, '%.12g' % D_fem_m, '%.12g' % D_fem_omega,
                    '%.10g' % eps, '%.10g' % (D_fem_omega / D_fem_m), path.name])
                print('n=%g Re=%g D_LBM=%.8f D_FEM_M=%.8f D_FEM_Omega=%.8f eps=%.2f%% covered=%d/%d (%.1fs)'
                      % (n, re, D_lbm, D_fem_m, D_fem_omega, eps,
                         covered.sum(), len(yy), time.time() - t0), flush=True)
    print('DONE ->', out_path)


if __name__ == '__main__':
    main()
