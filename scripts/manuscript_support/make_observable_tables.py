# -*- coding: utf-8 -*-
"""Compute a traceable kinetic-energy/speed table from archived N=128 fields.

This is used by the restructured main manuscript to separate the two area
normalizations and to replace the old wording 'total momentum content' by
'integrated kinetic energy'.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "01_geometry"))
from superellipse import Superellipse  # noqa: E402

DATA = ROOT / "05_dataset" / "data_all190"


def main():
    rows = []
    for path in sorted(DATA.glob("*.npz")):
        with np.load(path) as z:
            if int(z["N"]) != 128 or abs(float(z["Re"]) - 1000.0) > 1e-9:
                continue
            n = float(z["n"])
            ux = np.asarray(z["ux"], float)
            uy = np.asarray(z["uy"], float)
            fluid = np.asarray(z["fluid"]).astype(bool)
            X = np.asarray(z["X"], float)
            dx = float(abs(X[0, 1] - X[0, 0]))
            a_fluid = float(np.count_nonzero(fluid)) * dx * dx
            a_exact = Superellipse(n=n).area()
            ke = 0.5 * float(np.sum(ux[fluid] ** 2 + uy[fluid] ** 2)) * dx * dx
            umax = float(np.max(np.hypot(ux[fluid], uy[fluid])))
            rows.append(dict(case_id=path.stem, n=n, Re=1000.0, N=128,
                             A_fluid=a_fluid, A_exact=a_exact, KE=ke,
                             KE_over_A_fluid=ke / a_fluid,
                             KE_over_A_exact=ke / a_exact,
                             umax=umax, dx=dx))
    rows.sort(key=lambda r: r["n"])
    fields = list(rows[0])
    with (HERE / "observable_summary.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: ("%.12g" % v if isinstance(v, float) else v)
                        for k, v in r.items()})

    tex = ["\\begin{tabular}{@{}ccccc@{}}", "\\toprule",
           "$n$ & $KE$ & $KE/A_{\\rm fluid}$ & $KE/A(n)$ & $U_{\\max}/U_{\\rm lid}$ \\\\",
           "\\midrule"]
    for r in rows:
        tex.append("%g & %.5f & %.5f & %.5f & %.3f \\\\" %
                   (r["n"], r["KE"], r["KE_over_A_fluid"],
                    r["KE_over_A_exact"], r["umax"]))
    tex += ["\\bottomrule", "\\end{tabular}"]
    (HERE / "kinetic_table.tex").write_text("\n".join(tex), encoding="utf-8")
    print("wrote observable_summary.csv and kinetic_table.tex")


if __name__ == "__main__":
    main()
