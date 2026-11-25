# Jonctions : quantification, bilan énergétique et reformulation

## 1. Ce qui est établi : la condition aux limites est discontinue, sans régularisation

Code de production (lecture seule) :

* `02_LBM/lbm_geometry_grid.py` : le couvercle est sélectionné par `__y > 0__` strict ; la loi tangential est `__u_lid = U_lid (n_y, -n_x)__` ; les autres liens de paroi reçoivent `__u_w = 0__`.
* `01_geometry/superellipse.py` et `geometry_links.py` : aucun lissage, aucun `tanh`, aucune rampe, aucune longueur de régularisation `__ℓ_j__` n’est appliquée. La vitesse passe brutalement d’une valeur tangentielle non nulle à zéro aux deux jonctions `__(+/-1, 0)__`.

Il n’existe donc **aucune longueur physique de régularisation**, et rien qui reste fixe sous raffinement. Le cas choix B du referee s’applique : la dissipation est une grandeur numérique à coupure, définie par le masque de gradients, et non une mesure convergée de la dissipation physique totale.

Conséquence pour la limite carrée (referee #4.B1) : avec la loi tangentielle et `__y>0__`, la limite `__n→∞__` est un carré dont les **moitiés supérieures des parois latérales restent animées** (vers le bas à droite, vers le haut à gauche), les moitiés inférieures étant fixes. Ce n’est **pas** la cavité carrée de Ghia. Le contrôle à vitesse horizontale projetée est celui qui tend vers la paroi supérieure horizontalement mobile et les côtés fixes. Le texte de remplacement est donné dans `00_audit_questions/AUDIT_NOTES.md`.

## 2. Quantification de la dissipation de jonction (calcul nouveau)

Domaines : `__Ω_j(r_j) = ⋃_{k=1,2} B_{r_j}(x_{j,k}) ∩ Ω__`, avec `__x_{j,±} = (±1, 0)__` pour toute la famille superelliptique, `__r_j/L_c = 0.05, 0.10, 0.15__` (`__L_c = 2__`). Même intégrande `__φ = (1/Re)(2u_x²+2v_y²+(u_y+v_x)²)__` et même masque gradient-valide que la production ; `__f_junction = D_junction / D_mask__`.

`N=128` (extrait ; 39 lignes complètes dans `junction_budget.csv`) :

| `n` | `Re` | `__f_j(r=0.05L)__` | `__f_j(r=0.10L)__` | `__f_j(r=0.15L)__` |
|---:|---:|---:|---:|---:|
| 1.25 | 100 | 0.155 | 0.312 | 0.426 |
| 2.00 | 100 | 0.138 | 0.297 | 0.413 |
| 4.00 | 100 | 0.121 | 0.252 | 0.347 |
| 8.00 | 100 | 0.095 | 0.199 | 0.275 |
| 1.25 | 1000 | 0.116 | 0.253 | 0.367 |
| 2.00 | 1000 | 0.088 | 0.207 | 0.311 |
| 4.00 | 1000 | 0.081 | 0.175 | 0.258 |
| 8.00 | 1000 | 0.073 | 0.154 | 0.226 |

`N=256`, cas disponibles :

| `n` | `Re` | `__f_j(r=0.05L)__` | `__f_j(r=0.10L)__` | `__f_j(r=0.15L)__` |
|---:|---:|---:|---:|---:|
| 1.25 | 1000 | 0.162 | 0.302 | 0.423 |
| 2.00 | 1000 | 0.143 | 0.277 | 0.379 |
| 4.00 | 100 | 0.201 | 0.333 | 0.424 |
| 4.00 | 1000 | 0.126 | 0.236 | 0.324 |
| 8.00 | 1000 | 0.113 | 0.209 | 0.285 |

Lecture :

1. La contribution des jonctions est **importante pour toutes les géométries**, pas seulement pour le carré : entre 7 % et 16 % du `D_mask` pour le petit disque, et entre 23 % et 43 % pour le grand.
2. Elle **décroît avec `n`** à `Re` fixé : la pointe (`n=1.25`) est la plus affectée, le quasi-carré (`n=8`) la moins affectée. Ce résultat contredit l’idée que le problème des jonctions est spécifique au carré.
3. Elle dépend fortement du rayon choisi : le rapport entre `r=0.15L` et `r=0.05L` varie de 2.7 (`n=1.25`) à 2.9 (`n=8`). Il ne faut donc pas présenter un rayon unique comme une mesure canonique.
4. Sensibilité à la résolution : à `Re=1000, n=4`, `f_j(0.05L)` passe de 0.081 (`N=128`) à 0.126 (`N=256`) ; le résultat est donc qualitatif, pas convergé.

Le rapport `1.21–1.32` de la reconstruction par couche fantôme **ne doit pas** être présenté comme une mesure des jonctions : il concerne la correction de la couche pariétale omise par le stencil.

## 3. Tentative de fermeture du bilan sur domaine excisé : échec vérifié

J’ai implémenté le flux demandé sur les interfaces artificielles

```
F = (1/2)|u|²u + p u - 2 nu S.u,     p = (rho-1)/(3 U_lid²),  nu = 2/Re,
```

avec interpolation bilinéaire sur chaque cercle, normale pointant vers le disque, et arc limité au fluide.

Avant d’utiliser ce flux, j’ai testé l’identité discrète `__∇·F = −2φ__` sur `n=4, Re=1000, N=128` (`identity_check.csv`) :

| quantité | valeur |
|---|---:|
| `__∫ ∂_x A_x + ∂_y A_y__` (`A` = convection − travail visqueux) | −0.015523 |
| `__∫ ∇·(p u)__` | +0.128603 |
| `__∫ 2φ__` | +0.025590 |
| `__∫∇·F / (−∫2φ)__` | **−4.419** (attendu +1) |
| facteur de pression requis pour fermer | **−0.0783** (attendu +1) |

Les champs macroscopiques archivés `(rho, u)` **ne satisfont pas l’identité discrète**. Les valeurs de flux calculées sont donc marquées `*_unverified` dans le CSV et **ne doivent pas être utilisées** pour affirmer une fermeture. La cause la plus probable est que `rho` et `ux/uy` sont des champs moyennés dans le temps, enregistrés sans les populations `f` qui permettraient un bilan MEM cohérent au même instant.

**Décision** : retenir l’option B du referee #4.4 — reconnaître que le diagnostic est limité aux portions hors jonctions et ne constitue pas une vérification du bilan énergétique global. Une fermeture quantitative exigerait une instrumentation au niveau du solveur (populations `f`, puissance MEM sur le même domaine excisé), qui n’est pas disponible dans les archives.

## 4. Modifications rédactionnelles obligatoires

* Supprimer toute formulation du type « *the production power estimator is verified* » (supplément V4, l. 2258–2259) et la remplacer par : « *The lid-power estimate is only compared on the domain excluding the junction disks. Because the excised domain has artificial internal boundaries carrying convective, pressure and viscous work, and because the archived macroscopic fields do not satisfy the discrete energy identity, this comparison does not constitute a verification of the global power–dissipation balance.* »
* Dans le corps principal, limiter l’affirmation à : « *a substantial fraction of the discrete dissipation is localized in the junction disks, and that fraction decreases from the pointed to the square-like member of the family* ».
* Ajouter la phrase de portée : « *No junction regularization is applied in the production condition; the dissipation is defined by the gradient-valid mask and remains cutoff- and resolution-dependent.* »

## 5. Fichiers produits

* `junction_budget.py` — calcul reproductible, y compris le test d’identité.
* `junction_budget.csv` — 39 lignes ; `f_junction` fiable, colonnes de flux explicitement `*_unverified`.
* `identity_check.csv` — valeurs du test d’identité discrète.
