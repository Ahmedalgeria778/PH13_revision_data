# Validation FEM : dissipation intégrée exacte et gradients

Toutes les valeurs ci-dessous sont lues dans les CSV générés par
`fem_dissipation_validation.py` et `fem_gradient_reconstruction.py`.
L’interpréteur utilisé est Python 3.14 avec scikit-fem 12.0.2.

## 1. Solve et intégration

- 36 solves Taylor--Hood P2/P1 exécutés : n=[1.25, 2.0, 4.0, 8.0], Re=[100.0, 400.0, 1000.0], nrefs=[4, 5, 6].
- Convergence Picard : 36/36 convergés.
- $D_{\rm FEM}=2\nu\int_\Omega S(u_h):S(u_h)\,dA$ est assemblée avec la base P2, pas reconstruite par différences finies.

## 2. Sensibilité au maillage (différences directes, sans Richardson)

| $n$ | $Re$ | $D_4$ | $D_5$ | $D_6$ | $\|D_6-D_5\|/D_6$ |
|---:|---:|---:|---:|---:|---:|
| 1.25 | 100 | 0.270031 | 0.299718 | 0.327424 | 8.46\% |
| 1.25 | 400 | 0.097115 | 0.105302 | 0.112580 | 6.46\% |
| 1.25 | 1000 | 0.055193 | 0.059007 | 0.062231 | 5.18\% |
| 2 | 100 | 0.194142 | 0.209065 | 0.224821 | 7.01\% |
| 2 | 400 | 0.078211 | 0.081855 | 0.085848 | 4.65\% |
| 2 | 1000 | 0.047212 | 0.047671 | 0.049404 | 3.51\% |
| 4 | 100 | 0.204751 | 0.218250 | 0.233612 | 6.58\% |
| 4 | 400 | 0.082576 | 0.084824 | 0.088559 | 4.22\% |
| 4 | 1000 | 0.050261 | 0.049286 | 0.050635 | 2.66\% |
| 8 | 100 | 0.240096 | 0.252065 | 0.267256 | 5.68\% |
| 8 | 400 | 0.094144 | 0.094476 | 0.097819 | 3.42\% |
| 8 | 1000 | 0.056177 | 0.054124 | 0.054848 | 1.32\% |

La plage des changements relatifs $5\to6$ est 1.32\% à 8.46\%. La suite n’est pas présentée comme une suite de Richardson : les niveaux 4, 5 et 6 changent le maillage et la solution, et les différences sont rapportées telles quelles.

## 3. Reconstruction des gradients à partir des champs archivés

Les champs `fem_ux`/`fem_uy` archivés sont des échantillons sur grille LBM, pas les degrés de liberté P2. Le gradient exact est réévalué par les fonctions de forme aux mêmes points à partir d’un solve `nrefs=6` fraîchement exécuté. Le gradient de comparaison est donc explicitement une reconstruction par différences centrales.

| $n$ | $Re$ | points | $\epsilon_{\nabla u}$ | $\epsilon_S$ | $\epsilon_\phi$ | err. rel. $D$ |
|---:|---:|---:|---:|---:|---:|---:|
| 1.25 | 100 | 9488 | 6.88\% | 9.83\% | 25.05\% | 3.74\% |
| 1.25 | 400 | 9488 | 5.99\% | 8.46\% | 12.28\% | 2.21\% |
| 1.25 | 1000 | 9488 | 6.28\% | 8.57\% | 8.66\% | 1.45\% |
| 2 | 100 | 12288 | 4.19\% | 6.69\% | 10.85\% | 1.44\% |
| 2 | 400 | 12288 | 3.79\% | 5.59\% | 5.28\% | 0.76\% |
| 2 | 1000 | 12288 | 4.87\% | 6.31\% | 8.36\% | 1.00\% |
| 4 | 100 | 14444 | 4.02\% | 6.39\% | 11.30\% | 1.35\% |
| 4 | 400 | 14444 | 3.74\% | 5.49\% | 7.28\% | 0.82\% |
| 4 | 1000 | 14444 | 4.99\% | 6.44\% | 9.32\% | 1.11\% |
| 8 | 100 | 15168 | 3.80\% | 5.78\% | 10.74\% | 1.22\% |
| 8 | 400 | 15168 | 3.82\% | 5.42\% | 7.31\% | 0.93\% |
| 8 | 1000 | 15168 | 5.60\% | 7.22\% | 10.29\% | 1.39\% |

Nombre de points comparés : 9488 à 15168. Les erreurs de gradient restent $3.7\%$–$6.9\%$, ce qui montre qu’un champ échantillonné ne conserve pas les gradients exacts de la solution P2. Cette information est un test de post-traitement, pas une validation de la dissipation intégrale $D_{\rm FEM}$.

## 4. Portée

- L’intégration exacte confirme l’ordre de grandeur et la tendance en $n$ de la dissipation.
- Les changements de niveau de maillage sont rapportés directement : les niveaux absolus de $D$ à $N=128$ ne sont pas présentés comme convergés.
- Aucune extrapolation de Richardson n’est utilisée comme estimation quantitative.
- La comparaison FD/exact porte sur le support gradient-valide et ne doit pas être décrite comme une comparaison LBM/FEM indépendante.

## 5. Fichiers

* `fem_dissipation_validation.py` — solveur et assemblage de $D_{\rm FEM}$.
* `fem_gradient_reconstruction.py` — régénération de la table de gradients après correction de l’indexation des blocs de points.
* `fem_dissipation.csv`, `fem_mesh_refinement.csv`, `fem_gradient_reconstruction.csv` — tables exécutées.
