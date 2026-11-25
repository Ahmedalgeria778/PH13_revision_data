# Bilan additif cœur/paroi de la dissipation (réponse au referee #4.3 / #5.3)

## 1. Définition opératoire (aucune ambiguïté de dénominateur)

Pour chaque cas, le masque de gradients valides `__M__` est partitionné en

```
W_delta = M & { dist(x, Gamma) <= delta },      C_delta = M \ W_delta
```

avec `__delta = 0.025 L_c__` et `__0.05 L_c__`. Par construction `W_delta ∩ C_delta = ∅` et `W_delta ∪ C_delta = M`. En utilisant exactement la même intégrande que la production, `__φ = (1/Re)(2u_x² + 2v_y² + (u_y+v_x)²)__` sur `M`, et `__D = 2 Σ_M φ Δx²__` (`ν = 2/Re`) :

```
D_mask / A_mask  =  D_wall / A_mask  +  D_core / A_mask
```

Les trois grandeurs sont divisées par `__A_mask__` (aire du même masque), jamais par `A_core` ni par `A(n)`. C’est la relation demandée par le referee.

Données : 190 champs `N=128` (`data_all190`) et 63 champs `N=256` (`data_conv256` + `data_conv256_lowRe`), soit 253 cas × 2 épaisseurs = 506 lignes. Aucune simulation nouvelle.

## 2. Vérification de l’additivité

`max | D_mask − (D_wall + D_core) | = 2.78 × 10⁻¹⁷` sur les 506 lignes (précision machine). La relation est donc exacte, pas approximative.

## 3. Résultat central : la remontée de `D/A` est portée par le cœur

`N=128`, `δ = 0.025 L_c` (extrait ; valeurs complètes dans `core_wall_budget.csv`) :

| `Re` | `n` | `__D/A_mask__` | `__D_wall/A_mask__` | `__D_core/A_mask__` |
|---:|---:|---:|---:|---:|
| 300 | 2.50 | 0.016708 | 0.005961 | **0.010747** |
| 300 | 3.00 | **0.016167** | 0.005414 | 0.010754 |
| 300 | 4.00 | 0.016199 | 0.005076 | 0.011123 |
| 300 | 8.00 | 0.018008 | 0.005251 | 0.012756 |
| 500 | 2.50 | 0.012010 | 0.004816 | **0.007195** |
| 500 | 4.00 | **0.011501** | 0.004027 | 0.007474 |
| 500 | 8.00 | 0.012479 | 0.004130 | 0.008349 |
| 1000 | 2.00 | 0.008354 | 0.004409 | **0.003945** |
| 1000 | 4.00 | **0.007144** | 0.002868 | 0.004276 |
| 1000 | 8.00 | 0.007547 | 0.002910 | 0.004637 |

`N=256`, `δ = 0.025 L_c` :

| `Re` | `n` | `__D/A_mask__` | `__D_wall/A_mask__` | `__D_core/A_mask__` |
|---:|---:|---:|---:|---:|
| 300 | 2.00 | 0.021774 | 0.010879 | **0.010895** |
| 300 | 3.50 | **0.018923** | 0.008053 | 0.010870 |
| 300 | 8.00 | 0.020838 | 0.008051 | 0.012787 |
| 500 | 2.00 | 0.015854 | 0.008754 | **0.007100** |
| 500 | 3.75 | **0.013693** | 0.006318 | 0.007376 |
| 500 | 8.00 | 0.014716 | 0.006344 | 0.008372 |
| 1000 | 2.00 | 0.010289 | 0.006522 | **0.003768** |
| 1000 | 3.75 | **0.008789** | 0.004601 | 0.004188 |
| 1000 | 8.00 | 0.009199 | 0.004565 | 0.004635 |

Lecture :

1. `__D_wall/A_mask__` décroît globalement avec `n` (à `Re=1000`, `N=128` : 0.008475 à `n=1.25` → 0.002910 à `n=8`) ; il n’a **pas** de minimum à l’endroit du minimum de `D/A`.
2. `__D_core/A_mask__` a son minimum à `n≈2`–`2.5` puis **augmente** régulièrement jusqu’à `n=8`.
3. Le minimum de `D/A` est donc un minimum de **compensation** entre deux canaux aux tendances opposées, et non le minimum de l’un d’eux. La remontée au-delà du creux est portée par le cœur : par exemple à `Re=1000`, `N=256`, de `n=3.75` à `n=8`, `D_core/A` passe de 0.004188 à 0.004635 (+10.7 %) tandis que `D_wall/A` passe de 0.004601 à 0.004565 (−0.8 %).
4. Ce mécanisme est **identique aux deux résolutions et aux trois Reynolds**, et pour les deux épaisseurs de bande. C’est la démonstration additive qui manquait pour étayer l’« apprentissage de la redistribution spatiale ».

## 4. Sensibilité à l’épaisseur `__δ__` et mise à plat d’une affirmation

Avec `δ = 0.05 L_c`, la contribution pariétale est plus large mais la structure est la même : à `Re=1000`, `N=128`, `D_wall/A` passe de 0.011090 (`n=1.25`) à 0.004723 (`n=8`) avec un minimum vers `n=5`, tandis que `D_core/A` passe de 0.002911 à 0.002825 avec un minimum à `n=2`. Le minimum de `D_wall/A` dépend donc de `δ` et de `Re`.

**Conséquence rédactionnelle obligatoire** : il faut supprimer l’affirmation selon laquelle « la couche pariétale fixe la position du minimum » (manuscrit V4, l. 187–188 et l. 1335–1337). Ce que les données établissent est plus faible et plus précis : *la bande pariétale perd une part croissante de la dissipation quand `n` augmente, tandis que la contribution du cœur passe par un minimum plus tôt ; le creux de `D/A` résulte de la compensation des deux, et sa remontée est portée par le cœur.*

## 5. Limite de résolution (à ne pas confondre avec le mécanisme)

Les niveaux absolus ne sont pas convergés : à `Re=1000`, `n=4`, `D/A_mask` passe de 0.007144 (`N=128`) à 0.008797 (`N=256`), soit +23.1 %. La position *échantillonnée* du minimum passe de `n=4` à `n=3.75` (un pas de grille) entre les deux résolutions. Le mécanisme additif, lui, est conservé. Il faut donc présenter la compensation cœur/paroi comme un constat sur les grilles testées, et non comme une valeur de dissipation convergée ; les positions ajustées sont traitées séparément dans `05_minima_qualification`.

## 6. Fichiers produits

* `core_wall_budget.py` — calcul reproductible (506 lignes).
* `core_wall_budget.csv` — toutes les valeurs, résidu d’additivité inclus.
* `core_wall_budget_Re300_500_1000.png` / `.pdf` — 3 Reynolds × 2 résolutions, `D/A`, `D_wall/A`, `D_core/A`, deux épaisseurs de bande.
