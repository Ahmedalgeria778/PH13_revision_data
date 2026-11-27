# Audit des critiques et localisation exacte dans la version V4

Objet : `PH13_manuscript_revised_2026-11-21_V4.tex` (2396 lignes ; identique octet pour octet à `PH13_manuscript_revised.tex`) et `PH13_supplementary_revised_V2verrouille_2026-11-21.pdf` / `PH13_supplementary_revised.tex`. Le PDF principal compile à **52 pages** (la critique des 51 pages visait la V3). Les rapports détaillés des referees #4 et #5 ne sont pas présents dans le dossier : seuls les textes collés dans la demande sont disponibles. Aucune matrice de conformité littérale ne peut donc être certifiée pour ces deux rapports.

## 1. Points scientifiques bloquants (ordre imposé par la demande)

| Ordre | Point | Localisation V4 | État après calculs |
|---:|---|---|---|
| 1 | Limite carrée de la condition aux limites | manuscrit l. 294 et passage `n→∞` ; géométrie `01_geometry/superellipse.py`, `02_LBM/lbm_geometry_grid.py` | Corrigé dans la restructuration : voir §2 ci-dessous et `02_junction_energy_budget/junction_budget_report.md` §1 |
| 2 | Régularisation aux jonctions | `lbm_geometry_grid.py` (`y>0`, `u_lid=U(n_y,-n_x)`) | Aucune régularisation dans le code ; dissipation = grandeur à coupure |
| 3 | Courbure : test du cercle | supplément S15/S16 (l. 1331–1635), manuscrit l. 1340–1413, 1660–1663, 2060–2062 | **Corrigé** : `01_curvature_validation/` |
| 4 | Bilan énergétique aux jonctions | supplément S19, l. 2258–2259 (« power estimator is verified ») | **Non fermé** : `02_junction_energy_budget/` |
| 5 | Validation FEM des gradients et de `D` | supplément S7 (l. 689), manuscrit l. 438 | Fait : `03_FEM_dissipation_validation/` (rapport généré par `make_fem_report.py`) |
| 6 | Bilan additif cœur/paroi | manuscrit l. 1332–1337, 1401–1419 | **Fait** : `04_additive_core_wall_budget/` |
| 7 | Qualification des minima | manuscrit l. 64–66, 1476–1483, 1639–1652, 1895–1898 ; tableau V | Fait : `05_minima_qualification/` |
| 8 | Restructuration / longueur / DeepONet | voir §3 et §7 | Fait : `06_manuscript_restructure/` ; principal 17 pages / 7 sections, supplément enrichi 54 pages = original intact + addendum, 0 référence indéfinie |

## 2. Texte de remplacement pour la limite carrée (referee #4.B1)

Remplacer l’affirmation « *the classical square lid-driven cavity is recovered asymptotically* » par :

> As `n → ∞`, the superelliptic domain tends geometrically to the square `[-1,1]²`. However, the tangential wall-velocity prescription used in the present family does not converge to the classical square-cavity boundary condition. Since the moving portion is defined by `y > 0`, the upper halves of the vertical side walls remain in motion in the limiting geometry, with velocities directed downward on the right wall and upward on the left wall. The lower halves remain stationary. Consequently, the `n → ∞` limit represents a square domain with piecewise tangential wall motion, not the classical square cavity with a uniformly translating upper wall and stationary side walls. The classical square-cavity benchmark is therefore used as an independent verification case with a separately imposed boundary condition, rather than as a direct verification of the limiting member of the present family.

Préciser ensuite que le contrôle par vitesse horizontale projetée sur la tangente (`05_dataset/data_lid_projected`) est celui qui tend vers la loi de Ghia, et qu’il montre la sensibilité de la réponse à la loi de forçage sans séparer complètement aire, courbure et cinématique.

## 3. Localisations des suppressions DeepONet (corps principal)

| Zone | Lignes V4 | Action |
|---|---|---|
| Abstract | 72–74 | supprimer l’affirmation `R²` / DeepONet |
| Introduction | 163–171, 191–195 | supprimer la motivation opérateur |
| §2.2 | 263–278 | supprimer la description méthode DeepONet |
| Table I | 481–499 | supprimer la ligne DeepONet |
| Table II | 527 | supprimer la ligne correspondante |
| Figure 2 | 542–549 | supprimer le panneau DeepONet |
| §6 complète | 1676–1865 | **supprimer toute la section** |
| Discussion | 1904–1962, 2001–2009, 2021–2025 | supprimer les paragraphes DeepONet |
| Conclusions | 2075–2092 | supprimer le message opérateur |
| Remerciements / données / contributions | 2106–2162 | supprimer les références ML |
| Bibliographie ML | 2172–2309 | supprimer les entrées ML |

Une seule phrase peut subsister en perspectives : *“The reference database generated here also provides a basis for subsequent operator-learning studies of geometry extrapolation, which are beyond the scope of this fluid-mechanics analysis.”*

Le supplément contient également des sections opérateur (S13 environ). Cette instruction de retrait était l'état antérieur et est **remplacée par la décision finale du 2026-11-25** : le supplément original est conservé intégralement, sans suppression ni réécriture, et l'enrichissement est ajouté sous forme d'addendum. Les sections opérateur restent donc présentes dans `PH13_supplementary_enriched.tex` ; elles restent absentes du manuscrit principal.

## 4. Formulations à corriger partout

| Formulation V4 | Ligne(s) | Remplacement |
|---|---|---|
| « the drift is not a resolution artefact » | 64–66 | « the fitted minimum locations are similar on the matched grids, but absolute dissipation remains resolution-sensitive » |
| « the wall layer sets its location » | 64–66, 187–188, 1335–1337 | « the low-dissipation band results from opposing wall and core trends » (voir bilan additif) |
| « total momentum content » (`KE`) | 685–689 | « integrated kinetic energy » |
| « every relative statement in `n` is unaffected by resolution » | 1476–1483 | « the geometry-relative ordering is robust on the compared grids only » |
| « resolution-independent to about 2 % » | 1639–1652, 1895–1898 | « similar fitted locations on matched grids; absolute levels unresolved » |
| « onset / onset bracket / topologically distinct » | 1208, 1392, 2012, 1908–1912 | « threshold crossing at the 1 % detection level / sub-percent secondary extremum » |
| `D` plus faible avec `A` plus grand mais `D/A` plus grand | §5.3 | `D = A_mask (D/A_mask)` : avec `A₂>A₁, D₂≤D₁` on a nécessairement `D₂/A₂ < D₁/A₁` ; formule de remplacement dans le rapport #4 |
| `KE/A(n)` vs `D/A_mask(n)` | partout | distinguer explicitement les deux supports |

## 5. Environnement et traçabilité

Python du projet (ancien) : `C:\Users\user\Documents\travail pc taki_final\Default Project\Lid_driven_ondulation\.venv\Scripts\python.exe` (3.14.5) — NumPy, SciPy et Matplotlib disponibles, **scikit-fem absent**. Les calculs de cette révision ont donc été exécutés avec l’interpréteur de base `C:\Users\user\AppData\Local\Programs\Python\Python314\python.exe`, où scikit-fem 12.0.2, NumPy 2.5.3, SciPy 1.18.1, pandas 3.1.0 et Matplotlib 3.11.2 sont disponibles. Le solveur Taylor–Hood `04_reference_FEM/solver/navier_stokes_th.py` a été relancé dans cet interpréteur pour la validation FEM : voir `03_FEM_dissipation_validation/`.

Archives utilisées : `data_all190` (190 champs `N=128`, clés `ux, uy, rho, fluid, X, Y, fem_ux, fem_uy`), `data_conv256` + `data_conv256_lowRe` (63 champs `N=256`), `data_convHR` / `_extB` (18 champs `N=384/512`), `data_lid_projected` (15 cas).

Aucune simulation LBM nouvelle n’a été lancée. Les chiffres des rapports sous-dossiers proviennent de scripts exécutés et de fichiers CSV régénérés à partir des champs archivés. Les seules nouvelles simulations sont les solves Taylor–Hood P2/P1 de `03_FEM_dissipation_validation/`, utilisés uniquement pour la vérification (intégrale exacte de dissipation et gradients aux points LBM).

## 6. État historique de la restructuration (2026-11-24)

* `PH13_manuscript_physics_only.pdf` : **15 pages**, 8 figures, 8 tableaux, aucune référence LaTeX indéfinie, aucun avertissement `Overfull`/`Underfull`. DeepONet et tout lexique opérateur absent.
* `PH13_supplementary_physics_only.pdf` : **4 pages**, 4 tableaux, aucune référence indéfinie, aucun `Overfull` ; seulement 5 avertissements `Underfull \hbox` sans effet sur le contenu.
* Validation FEM finale : 36 solves P2/P1 convergés, 24 lignes de sensibilité de maillage et 12 lignes de reconstruction de gradients ; les supports comparés contiennent 9488 à 15168 points (après correction de l’indexation des blocs), pas les 192 points de l’ancienne table.
* Les tableaux LaTeX `fem_table.tex`, `fem_table_supp.tex` et `kinetic_table.tex` sont générés à partir des CSV et non saisis à la main.
* Le scan en lecture seule de `C:\Users\user\Documents` est consigné dans `DOCUMENTS_SCAN_FINDINGS.md` : seules les données traçables et non défectueuses sont utilisées.

## 7. État final de la révision scientifique ciblée (2026-11-25)

### 7.1 Documents

* `PH13_manuscript_physics_only.tex` : **17 pages**, **sept sections** (`Introduction`, `Geometry, boundary law and numerical method`, `Geometry-induced reorganization of the reference flow`, `Flow organization beyond the dissipation minimum`, `Why the area-normalized dissipation is non-monotonic`, `Resolution, fit windows and finite-element validation`, `Conclusions`) plus la sous-section `Scope and limitations`. Deux compilations successives ; aucune référence indéfinie. Seul subsiste l'avertissement bénin `microtype` sur la patch `footnote`.
* `PH13_supplementary_enriched.tex` : **54 pages**. Le préfixe est identique octet pour octet au supplément original. La seule différence est l'ajout de `\input{revision_addendum}` juste avant `\end{document}`. Aucune référence indéfinie ; deux avertissements bénins `hyperref` hérités de chaînes Unicode et des messages `ignored error: Infinite glue shrinkage found in box being split` hérités des longs tableaux originaux.
* `revision_addendum.tex` : neuf sous-sections nouvelles — support commun LBM/FEM, budget cœur/paroi étendu, courbure corrigée, audit FEM/jonctions, conventions d'énergie, `L_mov`/`P_lid`, inventaire des campagnes, ajustements/croisements et reproduction.

### 7.2 Résultats chiffrés verrouillés

* **Support commun** : après correction de l'indice de dérivation, $\varepsilon_D=0.06$–$6.52\%$ ; cas représentatif $n=4$, $Re=1000$ : $D_{\rm LBM}=0.0255896185899$, $D_{\rm FEM}=0.0246197180024$, $\varepsilon_D=3.9395\%$. La convention est $2\nu S:S$ des deux côtés, avec $\nu=2/Re$ en unités papier et $U_{\rm lid}=0.05$ pour LBM / $1$ pour FEM.
* **Ancienne colonne `rel. D error`** : $|D_{\rm FD,lattice}-D_{\rm exact,lattice}|/D_{\rm exact,lattice}$ ; elle ne mesure pas une validation LBM/FEM.
* **FEM** : maillages 4/5/6 = 1\,024/4\,096/16\,384 triangles et 4\,771/18\,755/74\,371 inconnues ; Picard $10^{-9}$ ; 36/36 solves convergés en 14–34 itérations. Jonction gauche $y=+1.22\times10^{-16}$ (mobile), jonction droite $y=0$ (fixe) sous le test strict $y>0$.
* **Courbure** : cercle unité $\kappa=1.000000$, $f_{\rm sharp}=0$ ; 190 lignes recalculées. Le seuil reste $\kappa_w\ge2\langle|\kappa|\rangle_\Gamma$ avec $w=0.05L_c$. La corrélation de Pearson $\kappa_{w,\rm rms}$/$D/A$ à $Re=1000$ passe de $+0.892$ à $+0.709$ ; $f_{\rm sharp}$ change de signe.
* **Budget cœur/paroi** : 506 lignes, résidu additif maximal $2.78\times10^{-17}$. Pour $Re=1000$, $N=256$, $\delta=0.05L_c$, $n=4\to8$, la part du cœur dans l'augmentation est $87.8\%$ ; la part absolue du cœur est $28.1\%$ à $n=4$ et $30.7\%$ à $n=8$. La plage disponible est $61.5$–$99.8\%$.
* **Campagnes** : `data_all190` = 190 champs ; `data_refine` = 50 champs et 8 valeurs de $Re$ ; $N=256$ = 63 champs et 62 appariés ; seul $(n,Re)=(4.25,300)$ est non apparié.
* **$L_{\rm mov}$** : $2.8789718432636$ ($n=1.25$), $\pi$ ($n=2$), $3.5088489717820$ ($n=4$), $3.7389869262423$ ($n=8$), avec validation losange/cercle/limite carrée.
* **$P_{\rm lid}$** : non coté comme grandeur vérifiée. L'archive contient 810 champs finaux convergés ; l'inventaire analysé en contient 380 ($190+50+28+50+13+12+24+13$). Aucun champ final n'a $f$ ; 148 checkpoints ont $f,it$ ; le rapport de flux archivé est $-4.419$ au lieu de $+1$. La valeur requise $P/\Phi$ varie de $4.268$ à $1.465$ entre $N=64$ et $512$, donc n'est pas convergée.
* **Bilan d'énergie** : distinction maintenue entre identité continue, bilan discret LBM exact non reconstruit et diagnostic de champs archivés non fermé. Convention $p_{\rm LBM}=c_s^2(\rho_{\rm LBM}-1)$, $c_s^2=1/3$, et $p=(\rho-1)/(3U_{\rm lid}^2)$ en unités papier.

### 7.3 Dépôt public

Le dépôt `https://github.com/Ahmedalgeria778/PH13_revision_data` contient les CSV, scripts, figures et rapports de cette révision, avec un `README.md` de reproduction. Il ne contient **ni source ni PDF du manuscrit**, ni les champs bruts `.npz`. Aucune nouvelle campagne LBM n'a été lancée ; seules ont été exécutées les opérations de post-traitement et les résolutions FEM ciblées.

---

## 8. État final de publication (2026-11-25) — remplace les sections 6 et 7

Les paragraphes précédents décrivent l'état intermédiaire avec supplément enrichi à addendum. La décision finale est la suivante et remplace toute formulation antérieure.

### 8.1 Documents

* `Article_File.tex` / `.pdf` du paquet de soumission : **22 pages**, **sept sections** ; zéro référence indéfinie ni avertissement `Overfull`. Le texte est physics-only : pas de DeepONet, pas d'Appendix A, pas de description provenance du supplément. La phrase exacte sur la variation de forme avec $n$ est présente dans l'Introduction. Le contrôle à couvercle projeté est une campagne LBM achevée de 13 champs appariés (rapports bruts $D/A_{\rm mask}$ projet/tangent $0.391$--$0.906$, rapport du bord $0.5$, rapports normalisés $0.782$--$1.813$, rapports $KE/A$ $0.768$--$2.291$) ; le minimum échantillonné passe de $n=4$ à $n=2$ mais n'est que borné entre $n=1.5$ et $n=4$. Les parts de jonction sont $7.3$--$15.5\%$ ($N=128$) et $11.3$--$20.1\%$ ($N=256$) à $r=0.05L_c$. Le lien GitHub et la mention MIT figurent uniquement dans Data availability.
* `Supplementary_Article_File.tex` / `.pdf` du paquet de soumission (copié dans le dépôt sous `PH13_supplementary_final.tex` / `.pdf`) : **32 pages**, **une seule partie**, sections S1--S17, Table S23, Fig. S13 et Tables S24--S31 ; zéro référence indéfinie ni avertissement `Overfull`, une ligne Alt text sous chaque figure et chaque tableau. Le supplément ne contient ni addendum, ni langage de révision, ni provenance, ni sections opérateur/DeepONet, ni figures de performance, ni graines, ni coûts d'entraînement, ni métriques OOD.
* Les fichiers `PH13_supplementary_enriched.*`, `revision_addendum.tex` et `PH13_supplementary_physics_only.*` sont conservés uniquement comme archives et ne sont plus les livrables autoritaires.

### 8.2 Correctifs scientifiques finaux

* Courbure : interpolation périodique complète, test du cercle $\kappa=1.000000$ et $f_{\rm sharp}=0$, 190 lignes recalculées ; corrélations $\kappa_{w,\rm rms}$/$D/A$ $=+0.834$ (`Re=100`) à $+0.709$ (`Re=1000`), Spearman $+0.115`, $f_{\rm sharp}<0$ à `Re=500,1000`.
* Diagnostic des coins : $0.20L_c$ pour la bande, $0.25L_c$ pour la recherche, $s_{\rm corner}$ en unités de $L=L_c/2$ ; pas de lignes extrapolées ; langage de seuil de détection $1\%$, sans « onset » ni « topologiquement distinct ».
* Support commun : $\varepsilon_D=0.06$--$6.52\%$ sur support identique ; le cas $n=4$, $Re=1000$ donne $\varepsilon_D=3.9395\%$. Le rapport $D_{\rm FEM}^{\Omega}/D_{\rm FEM}^{M}=1.63$--$2.06$ indique un effet de support ; aucun test FEM/LBM à support physique fixe $r_0>0$ n'a été exécuté.
* Bilan cœur/paroi : 506 lignes, résidu maximal $2.78\times10^{-17}$ ; $87.8\%$ est la part de la **montée** $n=4\to8$, pas la part absolue.
* $P_{\rm lid}$ : non coté ; 810 champs finaux convergés dans l'archive, 380 dans l'inventaire analysé, aucun avec $f$, 148 checkpoints avec $f,it$, rapport de flux $-4.419$.
* Convergence : les pentes des crossings $D/A(3)/D/A(4)$ sont d'environ $-95$, $-108$ et $-101$ en $Re$ par $\ln N$. Un test de scaling diffusif de la famille de production ($n=4$, $Re=1000$, $N=128/256/384/512$, $U_{\rm lid}=0.05\times128/N$, $\tau\simeq0.519$) a été achevé : à $r_0=0.5$ les valeurs coïncident avec la production à mieux que $5.3\times10^{-6}$ sur $N=128$--$512$ et l'ordre observé reste d'environ $1.01$. La baisse du nombre de Mach lattice ne supprime donc pas la dérive en résolution ; aucune explication Mach/acoustique n'est établie (Table S30, Sec. S17). Les ajustements $r=16h$ sont attribués au support $D_{\rm excl,16h}$, pas à un cutoff physique $r_0=0.5$. Un diagnostic à support de paroi physique fixe donne des variations de $D_{\rm core}$ de $2.8\%$ et $6.7\%$ de $N=128$ à $512$ contre $16.9\%$ pour $D_{r_0=0.5}$ ; la dérive restante est associée au support de paroi conservé après excision, non à une dérive des gradients de cœur sur un support physique fixe, sans certification de convergence continue (Table S31).
* Pas de fermeture globale d'énergie ; extrapolations Richardson uniquement diagnostiques.

### 8.3 Dépôt et installation

Le dépôt public contient maintenant le supplément final `.tex`/`.pdf`, les figures finales, les tables, les scripts, les rapports, un `README.md` anglais avec avis de copyright et une licence MIT anglaise dans `LICENSE`. Les dossiers `data/regime/` et `data/diffusive/` contiennent les diagnostics de convergence à rayon de jonction fixe et la comparaison production/diffusif, avec les scripts correspondants dans `scripts/final_revision/`. Il ne contient toujours ni source/PDF du manuscrit principal ni champs bruts `.npz`.

L'installation autoritaire est `08_operator_results/PH13_manuscript/`. Les livrables précédents ont été sauvegardés dans `backup_pre_publish_2026-11-25/`. Les journaux de compilation finaux `install_main_pass2.txt` et `install_supp_pass2.txt` ne contiennent aucune référence indéfinie ni erreur fatale.

### 8.4 Réponses aux referees

La lettre formelle anglaise est `RESPONSE_LETTER_FINAL.tex` / `.pdf`, avec les commentaires originaux en bleu foncé italique et les actions de révision en vert. Chaque item suit le couple « commentaire original → Revision made. ». Elle couvre les referees 1, 2, 4, 5 et 6. La matrice finale est `REVIEWER_RESPONSE_MATRIX.md`.

### 8.5 Paquet de soumission Physics of Fluids

Le dossier `08_operator_results/PH13_manuscript/submission_package/` contient les livrables prêts à téléverser, décrits dans `README_Submission.txt` :

* `Article_File.tex` / `.pdf` (22 p.) et `Supplementary_Article_File.tex` / `.pdf` (32 p.) : versions propres ; toutes les figures et tableaux sont incorporés dans les PDF à leur emplacement textuel exact (`[H]`), jamais après les références.
* `Marked-Up_Manuscript.tex` / `.pdf` (23 p.) et `Marked-Up_Supplementary.tex` / `.pdf` (34 p.) : vraies versions annotées, régénérées depuis la lignée des sources propres précédentes par différence mot à mot : ajouts en bleu, suppressions en rouge, texte inchangé en noir, avec enregistrement explicite du changement de titre. Les fichiers `.md` / `.html` obsolètes de la lettre de réponse ont été retirés.
* `Alt_Text.docx` : document Microsoft Word exigé par AIP pour le texte alternatif de toutes les figures et tables, avec miroir `Alt_Text.txt` ; la même ligne Alt text est imprimée sous chaque figure et chaque tableau des PDF propres et annotés.
* `RESPONSE_LETTER_FINAL.tex` / `.pdf` (14 p.) : lettre construite à partir des rapports originaux autoritaires ; 54 commentaires verbatim, chacun suivi d'une action de révision explicite.
* `Highlight_Image.tif` / `.jpeg` : image de mise en relief exactement 2404 x 1882 px à 300 dpi (8.0139 x 6.2739 in), issue de la plage de champs `Re=1000`.
* Liste des abréviations, nomenclature et section `Supplementary Material` insérée entre `Conclusions` et `Acknowledgments` dans l'article ; tous les acronymes sont définis à leur première apparition, y compris dans l'abstract.

### 8.6 Mise en forme finale du 2026-11-25

Une dernière passe de rédaction a retiré du corps de l'article et du supplément toute référence à des fichiers externes, à des chemins de données ou au dépôt GitHub. Les identifiants de campagnes, extensions `.csv`/`.npz`, noms de champs de métadonnées, inventaires de fichiers et mentions de points de contrôle ont été remplacés par des descriptions physiques ou des nombres de cas. Le lien GitHub et la licence MIT ne subsistent que dans les sections `Data availability`, comme autorisé. Le vocabulaire de révision, de contrôle qualité et de diagnostic « corrigé » a été reformulé en vocabulaire de publication (`dataset consistency checks`, `junction budget`, `field-data diagnostic`), sans retrait ni ajout de résultat physique. Les cinq PDF ont été recompilés deux fois : 22 p. (article propre), 32 p. (supplément propre), 23 p. (article annoté), 34 p. (supplément annoté), 14 p. (lettre de réponse), avec zéro référence indéfinie et aucun avertissement `Overfull`. Le texte extrait des PDF ne contient aucune commande LaTeX brute ; chaque figure et chaque tableau du supplément est suivi de sa ligne Alt text.

### 8.7 Provenance des figures après l'audit final

* `convergence_paroi.png` a été régénéré depuis `06_physics/etude_convergence_paroi.py` (`CASES=(1.25,300), (3,1000), (8,1000)`, `NS=64,128,256`) et synchronisé dans `submission_package/figs_new`, `submission_package/figs`, la racine de `PH13_manuscript`, `REV/figures/final_supplement`, `REV/figures` et `REV/supplement/figs_new` / `figs`. La copie finale fait 164 881 octets et a pour SHA-256 `3a27d81b88a417323ad0a9893a9389d8d8a4c11f7064db7d6864f8a5b509600b`; elle remplace l'ancienne figure six cas qui était incompatible avec la légende S14.
* `curve_kinetic_energy_vs_n.png` est produite par `scripts/final_revision/make_kinetic_energy_figure.py`, qui importe `_plot_curves` de `05_dataset/data/analyse_physique_mapping.py` et relit `06_physics/results_190/physics_observables.csv`. La copie finale fait 206 075 octets et a pour SHA-256 `c9d9f83ed5c7b92dd1512f83a96e8142376f4ca4e9065cfb93112a389033332a`.
* `fig_supp_corewall_Re100_500_1000.png` est désormais produite par `scripts/final_revision/make_corewall_supp_figure.py` depuis `data/core_wall/core_wall_budget.csv` (`N=128`, `Re=100,500,1000`, les deux épaisseurs de bande). `fig_supp_fem_junction_schematic.png` est produite par `scripts/final_revision/make_fem_junction_schematic.py` avec la convention archivée (`y=0` à droite, `y=+1.22e-16` à gauche, arrondi à deux chiffres significatifs dans l'étiquette). Leurs hachages sont donnés au §8.8.
* `figS11b_lbm_fem_convergence_N.png` est désormais produite par `scripts/final_revision/make_lbm_fem_convergence_figure.py` depuis `04_reference_FEM/validation/results/lbm_vs_fem_convergence/convergence.csv`. Le panneau (b) de Mach était déjà présent dans l'exemplaire archivé; la légende et le texte alternatif le mentionnent désormais explicitement, sans changer les valeurs.
* Les panneaux de vortex `Re=900`, `Re=950` et `Re=1000` restent les exemplaires autoritaires archivés dans `08_operator_results/PH13_manuscript_190/figs`; les champs NPZ sources sont présents, mais l'ancien chemin de script `results_190/vortices` est obsolète. Aucun résultat n'a été régénéré à partir de ce chemin.
* Les générateurs `make_common_support_figure.py` et `make_junction_cutoff_figure.py` n'écrivent pas tous les dossiers de copie finale; les exemplaires identiques ont été vérifiés octet pour octet après la passe de synchronisation décrite au §8.8.
* L'incrément exact `n=4 -> 8` du budget cœur/paroi vaut `0.0004025537906435731`, donc `0.000403` après arrondi. Les entrées du tableau affichées à six décimales donnent une différence visuelle de `0.000402`; le texte précise que l'incrément est calculé avant arrondi.

### 8.8 Impression noir et blanc et traçabilité des figures (2026-11-27)

Toutes les figures quantitatives à plusieurs séries ont été régénérées avec des marqueurs, des styles de trait ou des hachures distincts. La couleur ne constitue jamais le seul moyen de distinguer les cas; aucun point, aucune valeur et aucune convention physique n'ont été modifiés. Les champs scalaires et les cartes de vitesses conservent une colormap monotone, déjà lisible en niveaux de gris; les profils Ghia et les cartes de vortex conservaient déjà des marqueurs ouverts/solides distincts.

Générateurs modifiés : `scripts/manuscript_support/make_review_figures.py` (neuf figures), `scripts/final_revision/make_common_support_figure.py` (barres hachées), `scripts/final_revision/make_junction_cutoff_figure.py` (trois panneaux), `06_physics/etude_convergence_paroi.py` et sa copie `scripts/final_revision/etude_convergence_paroi.py`, ainsi que `05_dataset/data/analyse_physique_mapping.py::_plot_curves`. Générateurs ajoutés et vérifiés : `make_kinetic_energy_figure.py`, `make_corewall_supp_figure.py`, `make_fem_junction_schematic.py` et `make_lbm_fem_convergence_figure.py`, tous dans `scripts/final_revision/`.

Les deux figures dont le rapport largeur/hauteur aurait changé (`fig_supp_corewall_Re100_500_1000.png` et `fig_supp_fem_junction_schematic.png`) ont été complétées par des marges blanches afin de conserver exactement le rapport des exemplaires archivés; aucun contenu graphique n'a été rogné ni déplacé. Les exemplaires autoritaires sont dans `submission_package/figs_new`; des copies octet pour octet ont été synchronisées dans `submission_package/figs`, `REV/figures/final_supplement`, `REV/figures`, `REV/supplement/figs_new` et `REV/supplement/figs`. Les hachages SHA-256 des exemplaires `figs_new` sont :

| Figure | SHA-256 |
|---|---|
| `fig_core_wall_budget.png` | `56c179409d97891b97e5e37010ff337d41c3214a2e740574700891bd678ea0cb` |
| `fig_junction_share.png` | `5878ae71f6c4ca93fddef5828cde7424e506d15fa9e05bc7e3261636d63dd6b0` |
| `curve_dissipation_vs_n.png` | `1a1e4c0121e26d38fc25dd25d148dd2f991d8ecbb0b847c1993d7886cb90cbc6` |
| `map_dissipation.png` | `49ca4dada6b2c07a4ecc68b87e4930306078f678004c79cc067263ef9fe736d4` |
| `fig_fields_plate.png` | `0b0160df2b6e139a0d3dff171f74058bd5072be696e78294deb6b77c2d310ff9` |
| `fig_curvature.png` | `1b412e5ceed05703f43f35072f89fbdf868048c927da820854a398365afec9a2` |
| `fig_nearwall_large_axes.png` | `5cc225171b2c4ddaae6d8a3b9261027b880bddded0bd779192f13e3b3577cf52` |
| `fig_minima_windows.png` | `ca7502578c055edf5687d3b2871ff67afb22796b43cf1b10bdbf36392b6b2720` |
| `fig_fem_validation.png` | `2cf18490df20cf253f1a5fe9e72546ee9018f44cfcc190933d06be1ea849512a` |
| `fig_supp_common_support_dissipation.png` | `b520202336ac8e04d590198faac4b8b4f749e862f208fc0f6db4e0f2db78fafe` |
| `fig_junction_cutoffs.png` | `c47c12f8a3b54e2863899b23e4afb656e078d3f71e6e11eb9182a937fe7d80fd` |
| `convergence_paroi.png` | `3a27d81b88a417323ad0a9893a9389d8d8a4c11f7064db7d6864f8a5b509600b` |
| `curve_kinetic_energy_vs_n.png` | `c9d9f83ed5c7b92dd1512f83a96e8142376f4ca4e9065cfb93112a389033332a` |
| `fig_supp_corewall_Re100_500_1000.png` | `562561e7905b1eb036eb86f497a2f4a993ca799b80107710f745deb09294aa08` |
| `fig_supp_fem_junction_schematic.png` | `89d4c621e25968c62f58f72a5e15f17c3553c901a8a3357bc62dcffe0680d6cd` |
| `figS11b_lbm_fem_convergence_N.png` | `240ad8c121a04065578f3583817070b909d6dd78f4a07ddcdb02c572cedb7d3c` |

La légende et le texte alternatif de la figure S11b mentionnent maintenant le panneau de contrôle de la dépendance au Mach à $N$ fixe qui figurait déjà dans l'image archivée. `Alt_Text.txt` et `Alt_Text.docx` ont été régénérés après cette modification; le nombre d'entrées était alors de 13 pour l'article et 45 pour le supplément. La version finale porte le nombre d'entrées principales à 14 (voir §8.9).

### 8.9 Corrections finales de resoumission et vérification (2026-11-27)

Cette section consigne les seules corrections ciblées appliquées après l'audit final, sans nouvelle restructuration ni réécriture générale.

**Corrections ciblées appliquées.**

* La phrase de la section 2.2 sur $\mathrm{Ma}=0.0866$ est désormais explicitement limitée aux simulations de production. Le texte ajoute que le contrôle distinct de mise à l'échelle diffusive fait varier $U_{\rm lid}$ avec la résolution tout en maintenant $Re$ approximativement constant (article propre et article marqué).
* Le tableau I et sa légende comportent maintenant une ligne « Diffusive-scaling control » ($N=128$--$512$, quatre niveaux, $n=4$, $Re=1000$). Le tableau `tab:fixedwall` et son interprétation ont été insérés dans l'article principal : $D_{\rm diff}(r_0=0.5)=0.015117,0.017176,0.017859,0.018179$, $D_{\rm core}(0.05L_c)=0.008958,0.008796,0.008674,0.008714$ et $D_{\rm core}(0.10L_c)=0.002817,0.002675,0.002645,0.002641$ pour $N=128,256,384,512$. Le diagnostic est présenté comme une sensibilité spatiale, pas comme une certification du continu.
* L'inventaire S18 comprend une ligne « Diffusive-scaling control » et une note précisant que $N=128$ est le champ de production inchangé, réutilisé et non compté deux fois; seuls $N=256,384,512$ sont des runs additionnels. Cette clarification figure dans les deux versions du supplément.
* L'ordre invalide « increment-ratio order of $2.69$ » a été supprimé de toutes les sources de soumission. La cause était le calcul `log2(ip[0] / ip[2])` sur des intervalles inégaux dans `scripts/final_revision/analyse_diffusive_scaling.py`; la formule correcte est `log2(ip[0] / (ip[1] + ip[2]))`. Les ordres vérifiables sont $0.26/0.29$ ($r_0=0$), $1.01/1.01$ ($r_0=0.25$) et $1.04/1.04$ ($r_0=0.5$), les derniers correspondant aux doublements égaux $128/256/512$. Les deux copies de `diffusive_comparison.md` ont été corrigées.
* La lettre de réponse retire explicitement les anciennes discordances globales de $20.8\%$ et $31.3\%$ comme résultats de bilan énergétique validés, précise l'absence de flux d'interface et de distribution functions conservées, et indique qu'aucune clôture globale n'est revendiquée. Le compte du résumé y est désormais « approximately 238 words ».
* La section 7 a été remplacée par le texte proposé, que ce soit dans l'article propre ou en bleu dans l'article marqué. L'ancienne conclusion, y compris « support redistribution of viscous loss as the robust mechanism », ne subsiste que comme texte rouge supprimé dans `Marked-Up_Manuscript.tex`; elle n'apparaît dans aucune version propre ni dans aucun PDF propre.
* Les polices des figures 4, 5, 8 et 10 ont été agrandies (`fig_core_wall_budget.png`, `fig_junction_cutoffs.png`, `fig_minima_windows.png`, `fig_fem_validation.png`) sans modifier les données tracées. `make_junction_cutoff_figure.py` restaure exactement les dimensions archivées `(5073, 1577)` par `match_archived_aspect()`. Les rapports d'aspect vérifiés sont respectivement $2640/880$, $5073/1577$, $1640/880$ et $2400/920$, identiques aux exemplaires archivés. Les nouveaux hachages SHA-256 sont consignés au §8.8 et vérifiés 16/16 par `check_final_hashes.py`.
* Deux accolades surnuméraires dans les légendes des fichiers marqués (tableau I de `Marked-Up_Manuscript.tex` et tableau S18 de `Marked-Up_Supplementary.tex`) ont été corrigées avant la dernière compilation. La direction de synchronisation a été respectée : sources supplément/réponse de `submission_package` vers `REV`, et `Alt_Text.txt`/`.docx` de `REV` vers `submission_package`.

**Textes alternatifs et administration AIP.**

* `alt_text_pipeline.py` a été mis à jour pour 14 flottants principaux. Les textes alternatifs ont été régénérés puis synchronisés : 14 entrées pour l'article propre, 14 pour l'article marqué, 45 pour chaque supplément. `Alt_Text.txt` et `Alt_Text.docx` sont complets et présents dans `submission_package` et `REV/reports`.
* Les fichiers administratifs AIP sont présents et non vides dans `submission_package` : `Article_File.pdf`, `Supplementary_Article_File.pdf`, `RESPONSE_LETTER_FINAL.pdf`, `Marked-Up_Manuscript.pdf`, les sources `.tex` correspondantes, `Alt_Text.docx`, `Alt_Text.txt` et `Highlight_Image.jpeg`/`.tif`. `Marked-Up_Supplementary.pdf` y est également fourni.
* Les deux images de mise en évidence ont été ouvertes et vérifiées : `Highlight_Image.jpeg` (JPEG, RGB, $2404\times1882$, 998817 octets, SHA-256 `71a49bdf61632e36e7b918d419d265a7ee1975b4e5aea1a91219396bd4a8046c`) et `Highlight_Image.tif` (TIFF, RGB, $2404\times1882$, 2559460 octets, SHA-256 `bb3fb76c3cef050c5e70d069d08edf04419f78b2339647930a5b5ae3ed8af4d5`).
* Trois PDF de la soumission étaient verrouillés par des processus Windows locaux; les anciens exemplaires ont été renommés en `.locked-old`, les PDF ont été recompilés, puis les anciens exemplaires ont été supprimés. Aucun fichier `.locked-old` ne subsiste.

**Vérifications finales.**

* Les huit PDF ont été recompilés deux fois avec succès après les corrections d'accolades : article propre 23 pages, article marqué 25 pages, supplément propre 32 pages, supplément marqué 34 pages, lettre de réponse 14 pages, plus les trois copies `REV` (32, 34 et 14 pages). Aucune compilation ne présente d'erreur fatale.
* `verify_final_package.py` : tous les contrôles automatiques sont passés (textes alternatifs 14/45, absence de `??` sauf points d'interrogation légitimes, étiquettes uniques, journaux LaTeX propres, 4 tableaux et 10 figures dans l'article, chaînes critiques présentes et phrases interdites absentes).
* `verify_pdf_garble.py` : aucune chaîne corrompue interdite dans les huit PDF. Les seuls `?` sont ceux de la question légitime du titre et de la citation littérale d'une question de reviewer dans la lettre de réponse.
* `count_abstract_pdf2.py` : 238 tokens alphanumériques dans le résumé du PDF, soit moins que la limite de 250 mots; la lettre indique correctement « approximately 238 words ».
* `check_orders_all.py` : ordres recomputés $0.26/0.29$, $1.01/1.01$ et $1.04/1.04$, cohérents avec les sources corrigées.
* Après ces vérifications, les fichiers `.aux`, `.log`, `.out` et les dossiers `__pycache__` générés ont été supprimés, ainsi que le dossier temporaire `scripts/manuscript_support/figs_new`; seuls les exemplaires synchronisés dans `submission_package/figs_new`, `REV/figures`, `REV/figures/final_supplement`, `REV/supplement/figs` et `REV/supplement/figs_new` subsistent.

### 8.10 Correction de lisibilité de la figure S10 (2026-11-27)

*À la demande de l'auteur, seul le dessin de la figure S10 a été réagencé; la légende, le texte alternatif et les données scientifiques sont inchangés.*

* `scripts/final_revision/make_fem_junction_schematic.py` place désormais les définitions des symboles dans une légende distincte en pied de figure. Les deux annotations de jonction sont déportées à l'extérieur du cercle (texte à gauche de la jonction gauche, à droite de la jonction droite), et les étiquettes « moving upper arc » / « fixed lower arc » sont séparées de la légende. Un contrôle des boîtes englobantes après rendu confirme qu'aucune annotation, étiquette d'arc, jonction ou entrée de légende ne se superpose; toutes les boîtes restent dans le canevas conservé par `bbox_inches="tight"`.
* L'image finale fait exactement $1343\times978$ pixels, soit le rapport archivé $1343/978$. Son SHA-256 est `89d4c621e25968c62f58f72a5e15f17c3553c901a8a3357bc62dcffe0680d6cd` (il remplace `163bd8cd7f62c06bfd030c38c04806d64933c16a5b8cf3ee898c512e9b0a249b` au §8.8). Les six exemplaires (`submission_package/figs_new`, `submission_package/figs`, `REV/figures/final_supplement`, `REV/figures`, `REV/supplement/figs_new`, `REV/supplement/figs`) sont octet pour octet identiques.
* Les quatre PDF contenant S10 (`Supplementary_Article_File.pdf` et `Marked-Up_Supplementary.pdf` dans `submission_package`, ainsi que `supplement/PH13_supplementary_final.pdf` et `supplement/Marked-Up_Supplementary.pdf` dans `REV`) ont été recompilés deux fois; le pilote complet a reconstruit les huit PDF sans erreur fatale. Deux PDF ouverts dans un lecteur Windows local étaient verrouillés; ils ont été renommés en `.locked-old`, recompilés, puis les anciens exemplaires ont été supprimés.
* Vérifications relancées après cette correction : `verify_final_package.py` tous contrôles passés (textes alternatifs 14/45, 4 tableaux et 10 figures dans l'article, aucune étiquette dupliquée, journaux LaTeX propres); `verify_pdf_garble.py` aucune chaîne corrompue interdite; `check_final_hashes.py` 16/16 hachages conformes. Le résumé reste à 238 mots et les ordres à $0.26/0.29$, $1.01/1.01$, $1.04/1.04$.

### 8.11 Campagne A — supports physiques fixes (2026-11-27)

*Suite à la recommandation stratégique de l'auteur, aucune nouvelle simulation n'a été lancée. Cette section consigne uniquement un recalcul des champs archivés; les manuscrits, le supplément et la lettre de réponse restent inchangés.*

* `scripts/final_revision/campaign_a_fixed_support.py` inventorie 820 champs macroscopiques archivés (361 champs `production` primaires) et recalcule la dissipation sur $M_{\delta,r_0}=M_{\rm valid}\cap\{d(\mathbf x,\Gamma_n)>\delta\}\cap_j\{|\mathbf x-\mathbf x_j|>r_0\}$, avec $\delta/L_c\in\{0.025,0.05,0.10\}$ et $r_0\in\{0,0.03125,0.0625,0.125,0.25\}$. La distance $d$ est obtenue par `Superellipse.boundary_points(120000, arc_uniform=True)` et KD-tree en coordonnées physiques; le maillage n'intervient que via $h_N=2/(N-1)$. Les schémas (`production`, `diffusive`, `projected`, `snapshot`, `smoke`, `checkpoint`) et les doublons sont étiquetés, jamais fusionnés silencieusement.
* Livrables : `data/campaign_a/campaign_a_dissipation.csv` (12 300 lignes), `campaign_a_paired_differences.csv` (7 095 lignes), `campaign_a_minimum_stability.csv` (615 lignes), `campaign_a_annuli.csv` (126 lignes), `README_campaign_A.md`, quatre figures B&W dans `figures/campaign_a/` et leurs textes alternatifs. L'additivité $D_{\rm core}+D_{\rm wall}=D_{\rm base}$ est exacte à $5.6\times10^{-17}$ près.
* Pour $n=4$, $Re=1000$, $\delta/L_c=0.05$, $r_0=0.0625$, $D_{\rm core}$ vaut $0.008958$ ($N=128$), $0.008796$ ($256$), $0.008674$ ($384$) et $0.008714$ ($512$), soit une dérive de $2.8\%$ entre 128 et 512 et de $0.5\%$ entre 384 et 512. Sur le même support sans bande pariétale exclue, $D_{\rm base}$ passe de $0.024743$ à $0.032860$, ce qui situe l'essentiel de la dérive résiduelle dans la couche conservée près de la paroi.
* Les différences appariées gardent un signe stable aux grilles fines : $D_2/D_4\simeq0.497$, $D_3/D_4\simeq0.773$ et $D_4/D_8\simeq0.821$ à $N=512$ pour $\delta/L_c=0.05$ et $r_0=0.0625$. En revanche, seulement $19/41$ à $23/41$ des combinaisons support/résolution présentent un creux supérieur à deux fois l'écart max entre grilles consécutives. La conclusion prudente déjà insérée dans l'article (« broad low-dissipation range ») reste donc la seule défendable avant la Campagne B.
* Les couronnes de jonction montrent un $r|\mathbf S|$ borné entre environ $0.20$ et $0.35$ pour $r\in[0.0078,0.25]$ à $n=4$, $Re=1000$, tandis que $D_j(r,2r)$ croît avec $r$ et avec $N$. Ce résultat est un diagnostic préparatoire, pas une preuve de convergence; il motive les couronnes logarithmiques de la Campagne B.

