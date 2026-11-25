# -*- coding: utf-8 -*-
"""Targeted projected-lid control required by the second revision round.

The reference law is the tangential lid velocity u_w = U_lid t.  This targeted
control uses the impermeable horizontal projection u_w = U_lid (e_x.t) t, with
the same geometry, Reynolds number, lattice resolution and Mach number.  It
complements the earlier N=128 projected-lid archive with the requested design:

    N = 128: n = 1.5, 2, 4, 8 at Re = 100 and 1000 (seven new fields; the
             Re=1000 fields for n=2, 4, 8 already exist in the earlier archive);
    N = 256: n = 1.5, 2, 4, 8 at Re = 1000 and n = 4 at Re = 100, selected
             because those tangential partners exist in the archived campaigns.

Existing final fields are skipped.  Checkpoints permit resumption.  The output
is kept in a separate directory so that the earlier control archive is not
silently redefined.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parent.parent
for _p in (str(_ROOT / "01_geometry"), str(_ROOT / "02_LBM"),
           str(_ROOT / "05_dataset")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from superellipse import Superellipse  # noqa: E402
from solver_curved import CurvedLBM  # noqa: E402
import generate_convHR_campaign as hr  # noqa: E402

U_LID = 0.05
TOL = 1.0e-8
MAX_ITER = 1_000_000_000
OUT_DIR = _ROOT / "05_dataset" / "data_lid_projected_targeted"
MANIFEST = OUT_DIR / "manifest_lid_projected_targeted.csv"
EARLIER = _ROOT / "05_dataset" / "data_lid_projected"

# (n, Re, N).  Re=1000/n=2,4,8 already exist at N=128 in EARLIER.
CASES = (
    (1.5, 100.0, 128), (2.0, 100.0, 128),
    (4.0, 100.0, 128), (8.0, 100.0, 128), (1.5, 1000.0, 128),
    (1.5, 1000.0, 256), (2.0, 1000.0, 256),
    (4.0, 1000.0, 256), (8.0, 1000.0, 256), (4.0, 100.0, 256),
)


def case_id(n: float, Re: float, N: int) -> str:
    return (f"se_n{str(round(n, 2)).replace('.', 'p')}_"
            f"Re{int(round(Re))}_N{N}_proj")


def earlier_path(n: float, Re: float) -> Path:
    return EARLIER / f"{case_id(n, Re, 128)}.npz"


def plan() -> list[tuple[float, float, int]]:
    todo = []
    for n, Re, N in CASES:
        if N == 128 and earlier_path(n, Re).exists():
            continue
        if not (OUT_DIR / f"{case_id(n, Re, N)}.npz").exists():
            todo.append((n, Re, N))
    return todo


def simulate_one(job: tuple[float, float, int]):
    n, Re, N = job
    import numba
    numba.set_num_threads(1)
    cid = case_id(n, Re, N)
    dest = OUT_DIR / f"{cid}.npz"
    ckpt_path = OUT_DIR / f"{cid}_ckpt.npz"
    lock = OUT_DIR / f"{cid}.lock"
    if lock.exists():
        other = hr._lock_owner(lock)
        if other is not None and hr._pid_alive(other):
            return None
    lock.write_text(f"pid={os.getpid()} start={int(time.time())}",
                    encoding="utf-8")
    t0 = time.time()
    try:
        geom = Superellipse(n=n)
        lbm = CurvedLBM(geom, Re, N, U_lid=U_LID, max_iter=MAX_ITER, tol=TOL,
                        lid_mode="upper", L_char=N - 1,
                        lid_velocity="projected")
        start_it = 0
        if ckpt_path.exists():
            with np.load(ckpt_path) as c:
                saved_f = np.asarray(c["f"], dtype=np.float64)
                start_it = int(c["it"])
            if saved_f.shape != lbm.f.shape:
                raise RuntimeError(f"checkpoint incompatible: {ckpt_path}")
            lbm.f = np.ascontiguousarray(saved_f)
        hr.run_progress(lbm, MAX_ITER, TOL, 20000, cid,
                        ckpt_path=ckpt_path, ckpt_every=25000,
                        start_it=start_it)
        nu_lbm = U_LID * (N - 1) / Re
        tau_lbm = 3.0 * nu_lbm + 0.5
        omega = 1.0 / tau_lbm
        fluid = lbm.la.fluid.astype(bool)
        umax = float(np.hypot(lbm.ux[fluid], lbm.uy[fluid]).max())
        wall = time.time() - t0
        info = {
            "case": cid, "geometry": geom.metadata(),
            "run": {"solver": "lbm-mrt-bouzidi-linear", "Re": Re, "N": N,
                    "U_lid": U_LID, "nu_lbm": nu_lbm, "tau": tau_lbm,
                    "omega": omega, "L_char": N - 1, "iters": lbm.iters,
                    "residual": lbm.residual, "umax_lbm": umax,
                    "n_links": lbm.la.n_links, "lid_velocity": "projected"},
            "wall_time_s": wall,
            "provenance": "targeted revision control: projected horizontal lid",
        }
        out = {
            "case_id": cid, "n": n, "a": geom.a, "b": geom.b,
            "AR": geom.aspect_ratio, "L_c": geom.characteristic_length,
            "area_exact": geom.area(), "Re": Re, "N": N, "U_lid": U_LID,
            "nu_lbm": nu_lbm, "tau_lbm": tau_lbm, "omega_lbm": omega,
            "L_char": N - 1, "iters_lbm": lbm.iters,
            "residual_lbm": lbm.residual, "umax_lbm": umax,
            "n_fluid": int(fluid.sum()), "ux": lbm.ux, "uy": lbm.uy,
            "rho": lbm.rho, "fluid": lbm.la.fluid,
            "X": lbm.la.grid.X, "Y": lbm.la.grid.Y,
            "lid_velocity": "projected",
            "_meta": json.dumps(info),
        }
        np.savez_compressed(dest, **out)
        row = {"case_id": cid, "n": n, "Re": Re, "N": N, "U_lid": U_LID,
               "nu_lbm": nu_lbm, "tau_lbm": tau_lbm, "omega_lbm": omega,
               "L_char": N - 1, "iters_lbm": lbm.iters,
               "residual_lbm": lbm.residual, "umax_lbm": umax,
               "n_fluid": int(fluid.sum()), "wall_time_s": wall,
               "lid_velocity": "projected", "path": str(dest)}
        print(f"[targeted] OK {cid} iters={lbm.iters} "
              f"res={lbm.residual:.3e} wall={wall:.0f}s", flush=True)
        return row
    finally:
        lock.unlink(missing_ok=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=5)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    todo = plan()
    print(f"[targeted] {len(todo)} cases to run", flush=True)
    if args.dry_run:
        for job in todo:
            print("  " + case_id(*job))
        return 0
    if not todo:
        print("[targeted] nothing to do")
        return 0
    t_start = time.time()
    rows = []
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futures = {ex.submit(simulate_one, job): job for job in todo}
        for i, fut in enumerate(as_completed(futures), 1):
            row = fut.result()
            if row is None:
                continue
            rows.append(row)
            print(f"[targeted] {i}/{len(todo)} {row['case_id']} "
                  f"iters={row['iters_lbm']} t={row['wall_time_s']:.1f}s "
                  f"elapsed={time.time() - t_start:.0f}s", flush=True)
    old = []
    if MANIFEST.exists():
        with MANIFEST.open(newline="", encoding="utf-8") as fh:
            old = list(csv.DictReader(fh))
    all_rows = old + rows
    if all_rows:
        with MANIFEST.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(all_rows[0].keys()))
            writer.writeheader()
            writer.writerows(all_rows)
    print(f"[targeted] OK {len(rows)} cases -> {MANIFEST}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
