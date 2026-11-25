# -*- coding: utf-8 -*-
"""Recompute only the FD-vs-exact-FEM gradient reconstruction table.

The main fem_dissipation_validation.py writes the same table but also runs the
expensive mesh ladder.  This script reruns just the nrefs=6 solves needed for
the lattice reconstruction after a correction to the point-block indexing of
exact_grad_at().
"""
from __future__ import annotations

import csv
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "fv", HERE / "fem_dissipation_validation.py")
fv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fv)
Superellipse = fv.Superellipse  # imported by fv after its sys.path setup


def main():
    out = HERE / "fem_gradient_reconstruction.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        csv.writer(fh).writerow([
            "n", "Re", "N", "archived_nrefs", "n_points", "eps_grad",
            "eps_strain", "eps_phi", "rms_grad_exact", "rms_strain_exact",
            "D_FD_lattice", "D_exact_on_lattice", "rel_D_lattice_error",
            "source"])
    for n in fv.N_GRID:
        for re in fv.RE_GRID:
            res = fv.solve_cavity(Superellipse(n=n), Re=re, nrefs=6,
                                  U_lid=1.0, lid_mode="upper", verbose=False)
            rec = fv.reconstruct_from_archive(n, re, res)
            if rec is None:
                print("no archived field for n=%g Re=%g" % (n, re), flush=True)
                continue
            with out.open("a", newline="", encoding="utf-8") as fh:
                csv.writer(fh).writerow([
                    rec["n"], rec["Re"], rec["N"], rec["archived_nrefs"],
                    rec["n_points"], "%.10g" % rec["eps_grad"],
                    "%.10g" % rec["eps_strain"], "%.10g" % rec["eps_phi"],
                    "%.10g" % rec["rms_grad_exact"],
                    "%.10g" % rec["rms_strain_exact"],
                    "%.12g" % rec["D_FD_lattice"],
                    "%.12g" % rec["D_exact_on_lattice"],
                    "%.10g" % rec["rel_D_lattice_error"], rec["source"]])
            print("n=%g Re=%g: eps_grad=%.4f eps_phi=%.4f relD=%.4f" %
                  (n, re, rec["eps_grad"], rec["eps_phi"],
                   rec["rel_D_lattice_error"]), flush=True)


if __name__ == "__main__":
    main()
