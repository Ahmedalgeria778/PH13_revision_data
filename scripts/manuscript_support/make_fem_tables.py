# -*- coding: utf-8 -*-
"""Generate FEM LaTeX table fragments from the executed FEM CSVs."""
from __future__ import annotations

import csv
from pathlib import Path

OUT = Path(__file__).resolve().parent
BASE = OUT.parent / "03_FEM_dissipation_validation"


def read(name):
    with (BASE / name).open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def main():
    rows = read("fem_dissipation.csv")
    recon = read("fem_gradient_reconstruction.csv")
    rec_map = {(round(float(r["n"]), 4), round(float(r["Re"]), 2)): r for r in recon}

    # main table: Re=1000, four representative exponents
    L = ["\\begin{tabular}{@{}cccccc@{}}", "\\toprule",
         "$n$ & $D_{4}$ & $D_{5}$ & $D_{6}$ & $\\epsilon_{\\nabla u}$ & rel. $D$ error \\\\",
         "\\midrule"]
    for n in (1.25, 2.0, 4.0, 8.0):
        s = {int(r["nrefs"]): r for r in rows
             if abs(float(r["n"]) - n) < 1e-9 and abs(float(r["Re"]) - 1000) < 1e-9}
        if not all(k in s for k in (4, 5, 6)):
            continue
        rr = rec_map.get((round(n, 4), 1000.0), {})
        L.append("%g & %.6f & %.6f & %.6f & %s & %s \\\\" % (
            n, float(s[4]["D_FEM_exact"]), float(s[5]["D_FEM_exact"]),
            float(s[6]["D_FEM_exact"]),
            ("--" if not rr else "%.1f\\%%" % (100 * float(rr["eps_grad"]))),
            ("--" if not rr else "%.1f\\%%" % (100 * float(rr["rel_D_lattice_error"])))))
    L += ["\\bottomrule", "\\end{tabular}"]
    (OUT / "fem_table.tex").write_text("\n".join(L), encoding="utf-8")

    # supplement table: all n and Re, with mesh change 5 -> 6
    S = ["\\begin{tabular}{@{}cccccccc@{}}", "\\toprule",
         "$n$ & $Re$ & $D_{4}$ & $D_{5}$ & $D_{6}$ & $|\\Delta_{5\\to6}|/D_6$ "
         "& $\\epsilon_{\\nabla u}$ & rel. $D$ error \\\\", "\\midrule"]
    for re in (100.0, 400.0, 1000.0):
        for n in (1.25, 2.0, 4.0, 8.0):
            s = {int(r["nrefs"]): r for r in rows
                 if abs(float(r["n"]) - n) < 1e-9 and abs(float(r["Re"]) - re) < 1e-9}
            if not all(k in s for k in (4, 5, 6)):
                continue
            d4, d5, d6 = (float(s[k]["D_FEM_exact"]) for k in (4, 5, 6))
            rr = rec_map.get((round(n, 4), round(re, 2)), {})
            S.append("%g & %g & %.6f & %.6f & %.6f & %.2f\\%% & %s & %s \\\\" % (
                n, re, d4, d5, d6, 100 * abs(d6 - d5) / d6,
                ("--" if not rr else "%.2f\\%%" % (100 * float(rr["eps_grad"]))),
                ("--" if not rr else "%.2f\\%%" % (100 * float(rr["rel_D_lattice_error"])))))
    S += ["\\bottomrule", "\\end{tabular}"]
    (OUT / "fem_table_supp.tex").write_text("\n".join(S), encoding="utf-8")
    print("wrote fem_table.tex and fem_table_supp.tex")


if __name__ == "__main__":
    main()
