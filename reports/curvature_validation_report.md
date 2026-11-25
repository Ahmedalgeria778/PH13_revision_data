# Validation et correction de la courbure pariétale (Tableaux S15/S16)

## 1. Anomalie confirmée et cause exacte

Le test analytique échoue dans les scripts de production : pour `n=2`, `a=b=1`, la frontière est le cercle unité et `__kappa__ = 1` en tout point. Or la ligne `n=2, Re=100` de la Table S15 rapportait `__kappa_{w,max}=29.87__`, `__kappa_{w,rms}=4.015__`, `f_sharp=0.087`.

Cause : le même défaut est présent dans les trois scripts

* `08_operator_train/PH13_K5_campaign/PH13_16_make_nearwall_curvature_analysis.py` (l. 108–111),
* `06_physics/construire_figure_nearwall.py` (l. 126–129),
* `06_physics/etude_convergence_paroi.py` (l. 92–95) :

```python
half = self.n_samples // 2                     # 10000
s_half, th_half = s_d[:half], theta_d[:half]   # s_d a 200001 entrées
self.theta = np.interp(self.s % (half*self.ds), s_half, th_half)
self.theta[self.s >= half*self.ds] += math.pi
```

`s_d[:10000]` ne couvre que 5 % du périmètre. `__theta(s)__` est donc comprimé dans `[0, 0.314] ∪ [π, π+0.314]` au lieu de `[0, 2π)` ; les points `(x,y)` s’effondrent sur deux petits arcs et l’angle tangent obtenu par `np.gradient` est du bruit numérique. Noter que `__kappa_mean = 2π/L_Γ__` était correct (1.0000000000 pour le cercle) : seule la courbure *fenêtrée* était corruptible.

## 2. Correction appliquée

`curvature_fixed.py` :

1. `__theta(s)__` interpolation directe sur la table dense **complète**, prolongée périodiquement ;
2. angle tangent par différences centrales **périodiques** (`np.roll`), puis différence d’angle **enroulée** sur la fenêtre physique :
   `__kappa_w(s) = wrap(φ(s+w/2) − φ(s−w/2)) / w__` ;
3. ensemble « sharp » évalué par interpolation de `__kappa_w__` au point de paroi le plus proche (suppression de l’indexation approximative par `searchsorted`).

La fenêtre reste `__w = 0.05 L_c__` et le seuil `__kappa_w ≥ 2⟨|κ|⟩_Γ__` comme dans la production. Aucune simulation nouvelle ; 190 champs `N=128` relus.

## 3. Test analytique (cercle unité)

| `n_samples` | `w/L_c` | `__κ_{w,max}__` | `__κ_{w,rms}__` | `__f_sharp__` |
|---:|---:|---:|---:|---:|
| 2 000 | 0.01 | 1.000000 | 1.000000 | 0.000 |
| 2 000 | 0.05 | 1.000000 | 1.000000 | 0.000 |
| 5 000 | 0.05 | 1.000000 | 1.000000 | 0.000 |
| 20 000 | 0.05 | 1.000000 | 1.000000 | 0.000 |
| 50 000 | 0.10 | 1.000000 | 1.000000 | 0.000 |

**Test réussi** pour toutes les résolutions et fenêtres. Pour les 19 Reynolds du cas `n=2` : `κ_{w,max}: 29.874 → 1.00000`, `κ_{w,rms}: 4.015 → 1.00000`, `f_sharp: 0.0637 → 0.0000`.

## 4. Géométrie corrigée (indépendante de Re, comme attendu)

| `n` | `__κ_{w,max}__` | `__κ_{w,rms}__` | fraction « sharp » | `__⟨|κ|⟩_Γ__` |
|---:|---:|---:|---:|---:|
| 1.25 | 8.726 | 2.294 | 0.082 | 1.091 |
| 1.50 | 4.394 | 1.393 | 0.084 | 1.058 |
| 1.75 | 2.109 | 1.077 | 0.033 | 1.027 |
| 2.00 | **1.000** | **1.000** | **0.000** | 1.000 |
| 2.50 | 1.397 | 1.023 | 0.000 | 0.960 |
| 3.00 | 1.775 | 1.087 | 0.000 | 0.932 |
| 4.00 | 2.498 | 1.221 | 0.207 | 0.895 |
| 5.00 | 3.192 | 1.345 | 0.215 | 0.873 |
| 6.00 | 3.861 | 1.458 | 0.207 | 0.859 |
| 8.00 | 5.125 | 1.655 | 0.186 | 0.840 |

Le maximum est maintenant **minime au cercle** et maximal aux pointes (`n=1.25`) puis aux coins quasi-carrés (`n=8`), conformément à la géométrie. L’ensemble « sharp » est vide pour le cercle et pour `n=2.5–3`, et non vide aux pointes et aux coins : l’interprétation « pointes pour `n<2`, coins pour `n>2` » devient correcte.

## 5. Conséquences sur les corrélations de la Table S16

Corrélations de Pearson `r` (et Spearman `ρ` quand indiqué) entre chaque prédicteur et `D/A`, à `n` fixé (10 géométries) — ancien → corrigé :

| Prédicteur | `Re=100` (`r`) | `Re=500` (`r`) | `Re=1000` (`r`) | `Re=1000` (`ρ`) |
|---|---|---|---|---|
| `κ_{w,rms}` | +0.787 → +0.834 | +0.865 → +0.748 | +0.892 → **+0.709** | +0.794 → **+0.115** |
| `⟨κ⟩_D` | +0.983 → **+0.667** | +0.661 → +0.462 | +0.318 → +0.385 | −0.091 → **+0.636** |
| `f_sharp` | +0.802 → +0.794 | +0.333 → **−0.068** | +0.129 → **−0.238** | +0.152 → **−0.472** |
| `f_{0.025}` | +0.795 → +0.795 | +0.852 → +0.852 | +0.848 → +0.848 | +0.794 → +0.794 |

La légende actuelle de S16 (« `r` pour `⟨κ⟩_D` tombe de +0.983 à +0.310 ; sous `ρ` le même prédicteur change de signe à `Re=500`, atteignant −0.127 ») est donc **fausse** avec les valeurs corrigées : sous `ρ`, `⟨κ⟩_D` repasse à **+0.636** à `Re=1000`. L’affirmation selon laquelle `κ_{w,rms}`, `f_{0.025}` et `A` partagent la même ligne `ρ` (classements identiques) est également fausse (`ρ(κ_{w,rms})=+0.115` contre `ρ(f_{0.025})=+0.794`).

**Seul le prédicteur de bande pariétale `f_{0.025}` est inchangé** (il ne dépend pas de la courbure). C’est lui qui doit porter l’interprétation physique ; les affirmations fondées sur `κ_{w,max}`, `κ_{w,rms}`, `⟨κ⟩_D` et `f_sharp` doivent être retirées ou réécrites.

## 6. Assertions du manuscrit principal à réécrire (lignes du V4)

* L. 1341–1343 : `__κ_{w,max}=30.6 contre une moyenne de 1.09__` → `__8.73 contre 1.09__`.
* L. 1347–1348 : « la concentration relative de la courbure passe de 3.98 à 4.34 » → elle **diminue** de 2.10 à 1.97.
* L. 1368–1371 : « le maximum diminue faiblement de 30.57 à 27.77 » → le maximum est **non monotone**, 8.73 → 1.00 (cercle) → 5.13.
* L. 1373–1378 : « le maximum global de `f_sharp` se déplace de `n=1.25` vers `n=4` ; son minimum global est à `n=6` à tous les Re » → le minimum global est **zéro** pour `n=2, 2.5, 3` ; la transition se produit mais les amplitudes changent (0.108 → 0.136 à `Re=1000`).
* L. 1409–1413 : « `⟨κ⟩_D` passe de 0.879 (`n=1.25`) à 0.706 (`n=4`) puis remonte à 0.863 (`n=8`), les sites se rapprochent donc à nouveau des bords courbes » → valeurs corrigées à `Re=1000` : 0.851 → 0.726 → **0.428** ; **aucune remontée**, l’inférence est invalidée.
* L. 1660–1663 (figure) et L. 2060–2062 (conclusion) : mêmes correctifs.

La figure `PH13_nearwall_curvature_analysis.png` doit être régénérée à partir de `curvature_corrected_190.csv`.

## 7. Fichiers produits

* `curvature_fixed.py` — algorithme corrigé + test du cercle + recalcul des 190 cas.
* `curvature_corrected_190.csv` — 190 lignes, métriques corrigées, `D` et `f_{0.025}` inchangés.
* `curvature_before_after.csv` — comparaison ligne par ligne ancien/corrigé.

Les colonnes `__D__`, `__A_mask__`, `__D/A_mask__`, `f_{0.025}`, `f_{0.05}` sont identiques à la production à la précision d’arrondi : la correction ne touche que la courbure et les deux grandeurs qui en dépendent.
