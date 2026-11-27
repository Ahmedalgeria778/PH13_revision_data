# Campagne A -- supports physiques fixes

Aucune nouvelle simulation n'a ete lancee. Tous les champs macroscopiques
archives presentant `ux, uy, fluid, X, Y, N, Re, n` ont ete releves.

- champs inscrits dans le CSV : 820
- champs de production primaires : 361
- geometries : 17, Reynolds : 21, grilles : 64, 128, 256, 384, 512
- sommes de repetition : addsitivite D_core+D_wall=D_base, residu max 5.55e-17

## Definitions

$M_{r_0}=M_{\rm valid}\cap_j\{|\mathbf x-\mathbf x_j|>r_0\}$,
$M_{\delta,r_0}=M_{r_0}\cap\{d(\mathbf x,\Gamma_n)>\delta\}$.
$d$ est la distance euclidienne au bord superelliptique exact, echantillonne
par `Superellipse.boundary_points(120000, arc_uniform=True)` et interroge
par KD-tree en coordonnees physiques. Le mur est le complement de
$M_{\delta,r_0}$ dans $M_{r_0}$ : $D_{\rm core}+D_{\rm wall}=D_{\rm base}$ exactement.
$h_N=2/(N-1)$ et $D=2\sum_M(S_{\rm lbm}:S_{\rm lbm}/Re)h_N^2$.
Cette derniere convention est celle des tables deja publiees; elle est
proportionnelle a la dissipation physique et permet la comparaison directe.

## Schemes

`production`, `diffusive`, `projected`, `snapshot`, `smoke` et `checkpoint`
sont etiques dans le CSV. Les differences appariees n'utilisent que les
champs `production` primaires; l'echelle diffusive reste un ladder distinct.
Les doublons (memes n, Re, N) sont marques `primary=0` selon la priorite
des archives figees (`data`, `data_all190`, puis grilles de convergence).

## Resultats structurels

- 615 lignes de stabilite de minimum; 45.4% presentent
  un creux superieur a deux fois l'ecart maximal entre grilles consecutives.
- La conclusion finale sur l'optimum ne doit etre conservee que si ce test
  reste vrai pour plusieurs supports et aux grilles fines.
- 126 mesures de couronnes de jonction ont ete ajoutees pour
  preparer la Campagne B; elles ne prouvent pas a elles seules la singularite.

## Figures

Voir `figures/campaign_a/` et `figures/campaign_a/alt_text_campaign_A.txt`.
Toutes les figures sont en niveaux de gris avec marqueurs et styles de
ligne distincts, donc lisibles en noir et blanc.
