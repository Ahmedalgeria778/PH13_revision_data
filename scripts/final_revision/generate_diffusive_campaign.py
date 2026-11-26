# -*- coding: utf-8 -*-
"""Diffusive-scaling campaign for n=4, Re=1000 at N=128, 256, 384.

U_lid(N) = U_REF128 * 128 / N, with U_REF128 = 0.05.  With L_char = N-1
this keeps nu_lbm = U_lid (N-1) / Re essentially constant and lowers the
lattice Mach number as 1/N.  The fields are warm-started from the converged
production fields at the same N, rescaled to the target lattice velocity;
a coarse-grid diffusive seed was tested but relaxed more slowly.

Outputs:
  05_dataset/data_diffusive/*.npz, manifest_diffusive.csv
  06_physics/results_diffusive/diffusive_scaling.csv
"""
from __future__ import annotations

import argparse
import csv
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
for p in (ROOT / "01_geometry", ROOT / "02_LBM", ROOT / "06_physics"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from superellipse import Superellipse  # noqa: E402
from solver_curved import CurvedLBM, EX, EY, W, macroscopic  # noqa: E402
from etude_convergence_paroi import gradient_valid_mask  # noqa: E402

OUT_DIR = ROOT / "05_dataset" / "data_diffusive"
RES_DIR = ROOT / "06_physics" / "results_diffusive"
N_REF = 128
U_REF = 0.05
N_LIST = (128, 256, 384)
N = 4.0
RE = 1000.0
TOL = 1.0e-8
MAX_ITER = 900_000
PROGRESS_EVERY = 5000
CKPT_EVERY = 20000

SEEDS = {
    128: ROOT / "05_dataset/data_all190/se_n4p0_Re1000_N128.npz",
    256: ROOT / "05_dataset/data_conv256/se_n4p0_Re1000_N256.npz",
    384: ROOT / "05_dataset/data_convHR/se_n4p0_Re1000_N384.npz",
}
R0 = (0.0, 0.25, 0.5)
JUNC = ((1.0, 0.0), (-1.0, 0.0))


def case_id(Nn: int) -> str:
    return f"se_n4p0_Re1000_N{Nn}_diffusive"


def u_lid(Nn: int) -> float:
    return U_REF * N_REF / Nn


def equilibrium(lbm, rho, ux_l, uy_l):
    f = np.empty((9, lbm.N, lbm.N), dtype=np.float64)
    u2 = ux_l * ux_l + uy_l * uy_l
    for q in range(9):
        cu = EX[q] * ux_l + EY[q] * uy_l
        f[q] = W[q] * rho * (1.0 + 3.0 * cu + 4.5 * cu * cu - 1.5 * u2)
    return np.ascontiguousarray(f)


def warm_init(lbm, seed: Path) -> None:
    with np.load(seed) as z:
        ux = np.asarray(z["ux"], float)
        uy = np.asarray(z["uy"], float)
        rho = np.asarray(z["rho"], float)
    if ux.shape != (lbm.N, lbm.N):
        raise RuntimeError(f"seed shape mismatch: {seed}")
    lbm.f = equilibrium(lbm, rho, ux * lbm.U_lid, uy * lbm.U_lid)


def save_ckpt(path: Path, f: np.ndarray, it: int) -> None:
    tmp = path.with_name(path.stem + "_tmp.npz")
    np.savez_compressed(tmp, f=f, it=it)
    tmp.replace(path)


def run_one(Nn: int) -> dict:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cid = case_id(Nn)
    dest = OUT_DIR / f"{cid}.npz"
    ckpt = OUT_DIR / f"{cid}_ckpt.npz"
    if dest.exists():
        print(f"[diffusive] {cid} already complete, skipped", flush=True)
        return {"case": cid, "status": "skipped"}

    geom = Superellipse(n=N)
    lbm = CurvedLBM(geom, RE, Nn, U_lid=u_lid(Nn), max_iter=MAX_ITER,
                    tol=TOL, lid_mode="upper", L_char=Nn - 1)
    seed = SEEDS[Nn]
    print(f"[diffusive] {cid} seed <- {seed.name}", flush=True)
    warm_init(lbm, seed)
    start_it = 0
    if ckpt.exists():
        with np.load(ckpt) as z:
            f = np.asarray(z["f"], float)
            start_it = int(z["it"])
        if f.shape != lbm.f.shape:
            raise RuntimeError(f"checkpoint shape mismatch: {ckpt}")
        lbm.f = np.ascontiguousarray(f)
        print(f"[diffusive] {cid} resume at it={start_it}", flush=True)

    fluid = lbm.la.fluid.astype(bool)
    ux_prev = np.zeros((Nn, Nn))
    hist = []
    t0 = time.time()
    it = start_it
    for it in range(start_it + 1, MAX_ITER + 1):
        rho, ux, uy = lbm.step_fast()
        if it % CKPT_EVERY == 0:
            save_ckpt(ckpt, lbm.f, it)
        if it % 100 == 0 or it == 1:
            du = float(np.abs(ux - ux_prev)[fluid].max())
            ux_prev = ux.copy()
            hist.append((it, du))
            if it % PROGRESS_EVERY == 0 or it == 1:
                print(f"[diffusive] {cid} it={it} dUmax={du:.3e} "
                      f"t={time.time()-t0:.1f}s", flush=True)
            if du < TOL and it > 500:
                print(f"[diffusive] {cid} CONVERGED it={it} "
                      f"dUmax={du:.3e} t={time.time()-t0:.1f}s", flush=True)
                break
    rho, ux, uy = macroscopic(lbm.f)
    lbm.iters = it
    lbm.residual = hist[-1][1] if hist else float("nan")
    lbm.ux = ux / lbm.U_lid
    lbm.uy = uy / lbm.U_lid
    lbm.rho = rho
    np.savez_compressed(dest, ux=lbm.ux, uy=lbm.uy, rho=lbm.rho,
                        fluid=lbm.la.fluid, X=lbm.la.grid.X,
                        Y=lbm.la.grid.Y, Re=RE, N=Nn, iters=it,
                        residual=lbm.residual, n=N, U_lid=lbm.U_lid,
                        Re_u=1.0/RE, L_char=Nn-1,
                        nu_lbm=lbm.U_lid*(Nn-1)/RE, scheme="diffusive")
    ckpt.unlink(missing_ok=True)
    print(f"[diffusive] {cid} saved -> {dest.name}", flush=True)
    return {"case": cid, "status": "converged", "iters": it,
            "residual": lbm.residual, "wall_s": time.time()-t0}


def analyse(path: Path) -> dict:
    with np.load(path) as z:
        ux = np.asarray(z["ux"], float)
        uy = np.asarray(z["uy"], float)
        fluid = np.asarray(z["fluid"]).astype(bool)
        xx = np.asarray(z["X"], float)
        yy = np.asarray(z["Y"], float)
        Nn = int(z["N"])
        Re = float(z["Re"])
    dx = float(abs(xx[0, 1] - xx[0, 0]))
    valid = gradient_valid_mask(fluid)
    gx = np.full(ux.shape, np.nan); gy = np.full(ux.shape, np.nan)
    vx = np.full(ux.shape, np.nan); vy = np.full(ux.shape, np.nan)
    gx[1:-1, 1:-1] = (ux[1:-1, 2:] - ux[1:-1, :-2]) / (2*dx)
    vx[1:-1, 1:-1] = (uy[1:-1, 2:] - uy[1:-1, :-2]) / (2*dx)
    gy[1:-1, 1:-1] = (ux[2:, 1:-1] - ux[:-2, 1:-1]) / (2*dx)
    vy[1:-1, 1:-1] = (uy[2:, 1:-1] - uy[:-2, 1:-1]) / (2*dx)
    phi = (2*gx**2 + 2*vy**2 + (gy+vx)**2) / Re
    phi = np.where(valid, phi, 0.0)
    cell = dx*dx
    row = {"N": Nn, "h": dx}
    for r0 in R0:
        keep = valid.copy()
        for xj, yj in JUNC:
            keep &= np.hypot(xx-xj, yy-yj) > r0
        row[f"D_r{r0:g}"] = 2.0*float(np.sum(phi[keep]))*cell
        row[f"A_r{r0:g}"] = float(np.count_nonzero(keep))*cell
    return row


def main() -> int:
    global MAX_ITER
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--N-list", type=int, nargs="+", default=list(N_LIST),
                    help="resolutions to run (smoke tests may use a subset)")
    ap.add_argument("--max-iter", type=int, default=MAX_ITER)
    args = ap.parse_args()
    MAX_ITER = args.max_iter
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    RES_DIR.mkdir(parents=True, exist_ok=True)
    manifest = OUT_DIR / "manifest_diffusive.csv"
    if not manifest.exists():
        manifest.write_text(
            "case,n,Re,N,U_lid,nu_lbm,tau,seed,iters,residual,wall_s,status\n",
            encoding="utf-8")
    for Nn in args.N_list:
        info = run_one(Nn)
        p = OUT_DIR / f"{case_id(Nn)}.npz"
        if not p.exists():
            print(f"[diffusive] {case_id(Nn)} not available, abort", flush=True)
            return 1
        row = analyse(p)
        nu = u_lid(Nn) * (Nn - 1) / RE
        if info["status"] != "skipped":
            with manifest.open("a", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow([case_id(Nn), N, RE, Nn, u_lid(Nn), nu,
                            3*nu+0.5, SEEDS[Nn].name,
                            info.get("iters", ""), info.get("residual", ""),
                            info.get("wall_s", ""), info["status"]])
        print("[diffusive] " + " ".join(
            f"D_r{r0:g}={row[f'D_r{r0:g}']:.9f}" for r0 in R0), flush=True)
    rows = []
    for Nn in args.N_list:
        rows.append(analyse(OUT_DIR / f"{case_id(Nn)}.npz"))
    fields = ["N", "h"] + [k for r0 in R0 for k in
                           (f"D_r{r0:g}", f"A_r{r0:g}")]
    with (RES_DIR / "diffusive_scaling.csv").open(
            "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print("[diffusive] wrote " + str(RES_DIR / "diffusive_scaling.csv"),
          flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
