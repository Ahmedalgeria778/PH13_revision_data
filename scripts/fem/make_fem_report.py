# -*- coding: utf-8 -*-
"""Build fem_validation_report.md from the executed FEM CSVs only."""
from __future__ import annotations

import csv
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def main():
    ladder = read("fem_dissipation.csv")
    mesh = read("fem_mesh_refinement.csv")
    rec = read("fem_gradient_reconstruction.csv")

    def f(row, key):
        return float(row[key])

    lines = [
        "# Validation FEM : dissipation intégrée exacte et gradients",
        "",
        "Toutes les valeurs ci-dessous sont lues dans les CSV générés par",
        "`fem_dissipation_validation.py` et `fem_gradient_reconstruction.py`.",
        "L’interpréteur utilisé est Python 3.14 avec scikit-fem 12.0.2.",
        "",
        "## 1. Solve et intégration",
        "",
        f"- {len(ladder)} solves Taylor--Hood P2/P1 exécutés : "
        f"n={sorted(set(f(r, 'n') for r in ladder))}, "
        f"Re={sorted(set(f(r, 'Re') for r in ladder))}, "
        f"nrefs={sorted(set(int(r['nrefs']) for r in ladder))}.",
        f"- Convergence Picard : {sum(int(r['converged']) for r in ladder)}/{len(ladder)} convergés.",
        "- $D_{\\rm FEM}=2\\nu\\int_\\Omega S(u_h):S(u_h)\\,dA$ est assemblée avec la base P2, "
        "pas reconstruite par différences finies.",
        "",
        "## 2. Sensibilité au maillage (différences directes, sans Richardson)",
        "",
        "| $n$ | $Re$ | $D_4$ | $D_5$ | $D_6$ | $\\|D_6-D_5\\|/D_6$ |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    D = {(f(r, "n"), f(r, "Re"), int(r["nrefs"])): f(r, "D_FEM_exact") for r in ladder}
    for n in sorted(set(f(r, "n") for r in ladder)):
        for re in sorted(set(f(r, "Re") for r in ladder)):
            if all((n, re, k) in D for k in (4, 5, 6)):
                d4, d5, d6 = (D[(n, re, k)] for k in (4, 5, 6))
                lines.append(f"| {n:g} | {re:g} | {d4:.6f} | {d5:.6f} | {d6:.6f} | "
                             f"{100*abs(d6-d5)/d6:.2f}\\% |")
    lines += [
        "",
        f"La plage des changements relatifs $5\\to6$ est "
        f"{100*min(f(r,'rel_change') for r in mesh if r['nrefs_coarse']=='5'):.2f}\\% à "
        f"{100*max(f(r,'rel_change') for r in mesh if r['nrefs_coarse']=='5'):.2f}\\%. "
        "La suite n’est pas présentée comme une suite de Richardson : les niveaux 4, 5 et 6 "
        "changent le maillage et la solution, et les différences sont rapportées telles quelles.",
        "",
        "## 3. Reconstruction des gradients à partir des champs archivés",
        "",
        "Les champs `fem_ux`/`fem_uy` archivés sont des échantillons sur grille LBM, "
        "pas les degrés de liberté P2. Le gradient exact est réévalué par les fonctions de forme "
        "aux mêmes points à partir d’un solve `nrefs=6` fraîchement exécuté. Le gradient de comparaison "
        "est donc explicitement une reconstruction par différences centrales.",
        "",
        "| $n$ | $Re$ | points | $\\epsilon_{\\nabla u}$ | $\\epsilon_S$ | "
        "$\\epsilon_\\phi$ | err. rel. $D$ |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in rec:
        lines.append(f"| {f(r,'n'):g} | {f(r,'Re'):g} | {int(r['n_points'])} | "
                     f"{100*f(r,'eps_grad'):.2f}\\% | {100*f(r,'eps_strain'):.2f}\\% | "
                     f"{100*f(r,'eps_phi'):.2f}\\% | {100*f(r,'rel_D_lattice_error'):.2f}\\% |")
    lines += [
        "",
        f"Nombre de points comparés : {min(int(r['n_points']) for r in rec)} à "
        f"{max(int(r['n_points']) for r in rec)}. Les erreurs de gradient restent "
        f"${100*min(f(r,'eps_grad') for r in rec):.1f}\\%$–"
        f"${100*max(f(r,'eps_grad') for r in rec):.1f}\\%$, ce qui montre qu’un champ "
        "échantillonné ne conserve pas les gradients exacts de la solution P2. "
        "Cette information est un test de post-traitement, pas une validation "
        "de la dissipation intégrale $D_{\\rm FEM}$.",
        "",
        "## 4. Portée",
        "",
        "- L’intégration exacte confirme l’ordre de grandeur et la tendance en $n$ de la dissipation.",
        "- Les changements de niveau de maillage sont rapportés directement : les niveaux absolus "
        "de $D$ à $N=128$ ne sont pas présentés comme convergés.",
        "- Aucune extrapolation de Richardson n’est utilisée comme estimation quantitative.",
        "- La comparaison FD/exact porte sur le support gradient-valide et ne doit pas être "
        "décrite comme une comparaison LBM/FEM indépendante.",
        "",
        "## 5. Fichiers",
        "",
        "* `fem_dissipation_validation.py` — solveur et assemblage de $D_{\\rm FEM}$.",
        "* `fem_gradient_reconstruction.py` — régénération de la table de gradients après correction "
        "de l’indexation des blocs de points.",
        "* `fem_dissipation.csv`, `fem_mesh_refinement.csv`, `fem_gradient_reconstruction.csv` — tables exécutées.",
        "",
    ]
    (HERE / "fem_validation_report.md").write_text("\n".join(lines), encoding="utf-8")
    print("wrote", HERE / "fem_validation_report.md")


if __name__ == "__main__":
    main()
