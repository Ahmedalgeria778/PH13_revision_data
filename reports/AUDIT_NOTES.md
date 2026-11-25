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

* **Support commun** : $\varepsilon_D=0.72$–$20.02\%$ sur 9\,488–15\,168 nœuds du masque ; $D_{\rm FEM}^{\Omega}/D_{\rm FEM}^{M}=1.63$–$2.06$. La convention est $2\nu S:S$ des deux côtés, avec $\nu=2/Re$ en unités papier et $U_{\rm lid}=0.05$ pour LBM / $1$ pour FEM.
* **Ancienne colonne `rel. D error`** : $|D_{\rm FD,lattice}-D_{\rm exact,lattice}|/D_{\rm exact,lattice}$ ; elle ne mesure pas une validation LBM/FEM.
* **FEM** : maillages 4/5/6 = 1\,024/4\,096/16\,384 triangles et 4\,771/18\,755/74\,371 inconnues ; Picard $10^{-9}$ ; 36/36 solves convergés en 14–34 itérations. Jonction gauche $y=+1.22\times10^{-16}$ (mobile), jonction droite $y=0$ (fixe) sous le test strict $y>0$.
* **Courbure** : cercle unité $\kappa=1.000000$, $f_{\rm sharp}=0$ ; 190 lignes recalculées. Le seuil reste $\kappa_w\ge2\langle|\kappa|\rangle_\Gamma$ avec $w=0.05L_c$. La corrélation de Pearson $\kappa_{w,\rm rms}$/$D/A$ à $Re=1000$ passe de $+0.892$ à $+0.709$ ; $f_{\rm sharp}$ change de signe.
* **Budget cœur/paroi** : 506 lignes, résidu additif maximal $2.78\times10^{-17}$. Pour $Re=1000$, $N=256$, $\delta=0.05L_c$, $n=4\to8$, la part du cœur dans l'augmentation est $87.8\%$ ; la part absolue du cœur est $28.1\%$ à $n=4$ et $30.7\%$ à $n=8$. La plage disponible est $61.5$–$99.8\%$.
* **Campagnes** : `data_all190` = 190 champs ; `data_refine` = 50 champs et 8 valeurs de $Re$ ; $N=256$ = 63 champs et 62 appariés ; seul $(n,Re)=(4.25,300)$ est non apparié.
* **$L_{\rm mov}$** : $2.8789718432636$ ($n=1.25$), $\pi$ ($n=2$), $3.5088489717820$ ($n=4$), $3.7389869262423$ ($n=8$), avec validation losange/cercle/limite carrée.
* **$P_{\rm lid}$** : non coté comme grandeur vérifiée. 810 champs finaux sans $f$ ; 148 checkpoints avec $f,it$ ; le rapport de flux archivé est $-4.419$ au lieu de $+1$. La valeur requise $P/\Phi$ varie de $4.268$ à $1.465$ entre $N=64$ et $512$, donc n'est pas convergée.
* **Bilan d'énergie** : distinction maintenue entre identité continue, bilan discret LBM exact non reconstruit et diagnostic de champs archivés non fermé. Convention $p_{\rm LBM}=c_s^2(\rho_{\rm LBM}-1)$, $c_s^2=1/3$, et $p=(\rho-1)/(3U_{\rm lid}^2)$ en unités papier.

### 7.3 Dépôt public

Le dépôt `https://github.com/Ahmedalgeria778/PH13_revision_data` contient les CSV, scripts, figures et rapports de cette révision, avec un `README.md` de reproduction. Il ne contient **ni source ni PDF du manuscrit**, ni les champs bruts `.npz`. Aucune nouvelle campagne LBM n'a été lancée ; seules ont été exécutées les opérations de post-traitement et les résolutions FEM ciblées.

---

## 8. État final de publication (2026-11-25) — remplace les sections 6 et 7

Les paragraphes précédents décrivent l'état intermédiaire avec supplément enrichi à addendum. La décision finale est la suivante et remplace toute formulation antérieure.

### 8.1 Documents

* `PH13_manuscript_physics_only.tex` / `.pdf` : **19 pages**, **sept sections** ; zéro référence indéfinie. Le texte est physics-only : pas de DeepONet, pas d'Appendix A, pas de description provenance du supplément. La phrase exacte sur la variation de forme avec $n$ est présente dans l'Introduction. Le contrôle à couvercle projeté est une définition cinématique uniquement. Le lien GitHub et la mention MIT figurent dans Data availability.
* `PH13_supplementary_final.tex` / `.pdf` : **22 pages**, **une seule partie**, sections S1--S15 ; zéro référence indéfinie, texte Alt sous chaque légende. Le supplément ne contient ni addendum, ni langage de révision, ni provenance, ni sections opérateur/DeepONet, ni figures de performance, ni graines, ni coûts d'entraînement, ni métriques OOD.
* Les fichiers `PH13_supplementary_enriched.*`, `revision_addendum.tex` et `PH13_supplementary_physics_only.*` sont conservés uniquement comme archives et ne sont plus les livrables autoritaires.

### 8.2 Correctifs scientifiques finaux

* Courbure : interpolation périodique complète, test du cercle $\kappa=1.000000$ et $f_{\rm sharp}=0$, 190 lignes recalculées ; corrélations $\kappa_{w,\rm rms}$/$D/A$ $=+0.834$ (`Re=100`) à $+0.709$ (`Re=1000`), Spearman $+0.115`, $f_{\rm sharp}<0$ à `Re=500,1000`.
* Diagnostic des coins : $0.20L_c$ pour la bande, $0.25L_c$ pour la recherche, $s_{\rm corner}$ en unités de $L=L_c/2$ ; pas de lignes extrapolées ; langage de seuil de détection $1\%$, sans « onset » ni « topologiquement distinct ».
* Support commun : $\varepsilon_D=0.72$--$20.02\%$ sur 9\,488--15\,168 nœuds ; $D_{\rm FEM}^{\Omega}/D_{\rm FEM}^{M}=1.63$--$2.06$.
* Bilan cœur/paroi : 506 lignes, résidu maximal $2.78\times10^{-17}$ ; $87.8\%$ est la part de la **montée** $n=4\to8$, pas la part absolue.
* $P_{\rm lid}$ : non coté ; 810 champs finaux sans $f$, 148 checkpoints avec $f,it$, rapport de flux $-4.419$.
* Pas de fermeture globale d'énergie ; extrapolations Richardson uniquement diagnostiques.

### 8.3 Dépôt et installation

Le dépôt public contient maintenant le supplément final `.tex`/`.pdf`, les figures finales, les tables, les scripts, les rapports, un `README.md` anglais avec avis de copyright et une licence MIT anglaise dans `LICENSE`. Il ne contient toujours ni source/PDF du manuscrit principal ni champs bruts `.npz`.

L'installation autoritaire est `08_operator_results/PH13_manuscript/`. Les livrables précédents ont été sauvegardés dans `backup_pre_publish_2026-11-25/`. Les journaux de compilation finaux `install_main_pass2.txt` et `install_supp_pass2.txt` ne contiennent aucune référence indéfinie ni erreur fatale.

### 8.4 Réponses aux referees

La lettre formelle anglaise est `RESPONSE_LETTER_FINAL.tex` / `.pdf`, avec les questions en bleu foncé et les réponses en noir. Chaque item suit maintenant le couple « commentaire original → Revision made. » (ou « Justification for no change. » pour le referee 3). Elle couvre les referees 1, 2, 4, 5 et 6 ; aucun rapport séparé du referee 3 n'a été fourni, et cette lacune est explicitement conservée. La matrice finale est `REVIEWER_RESPONSE_MATRIX.md`.

### 8.5 Paquet de soumission Physics of Fluids

Le dossier `08_operator_results/PH13_manuscript/submission_package/` contient les livrables prêts à téléverser, décrits dans `README_Submission.txt` :

* `Article_File.tex` / `.pdf` et `Supplementary_Article_File.tex` / `.pdf` : versions propres ; toutes les figures et tableaux sont incorporés dans le PDF à leur emplacement textuel exact (`[H]`), jamais après les références.
* `Marked-Up_Manuscript.tex` / `.pdf` (21 p.) et `Marked-Up_Supplementary.tex` / `.pdf` (23 p.) : versions annotées générées contre les soumissions précédentes des 29 et 25 septembre 2026 (texte neuf/révisé en bleu, texte inchangé en noir, retraits résumés en prose propre en fin de document), car `latexdiff` n'était pas utilisable (Perl sans `Algorithm::Diff`). Un premier jet imprimait le code LaTeX brut des lignes supprimées dans un environnement `verbatim` ; il a été remplacé. Le texte extrait des quatre PDF ne contient aucune commande LaTeX brute.
* `Alt_Text.txt` : texte alternatif de toutes les figures et tables ; le supplément imprime aussi l'Alt text sous chaque légende.
* `RESPONSE_LETTER_FINAL.pdf` (avec `.tex`, `.md`, `.html`) et `Highlight_Image.tif` / `.jpeg` : image de mise en relief exactement 2404 x 1882 px à 300 dpi (8.0139 x 6.2739 in), issue de la plage de champs `Re=1000`.
* Liste des abréviations, nomenclature et section `Supplementary Material` insérée entre `Conclusions` et `Acknowledgments` dans l'article ; tous les acronymes sont définis à leur première apparition, y compris dans l'abstract.

### 8.6 Mise en forme finale du 2026-11-25

Une dernière passe de rédaction a retiré du corps de l'article et du supplément toute référence à des fichiers externes, à des chemins de données ou au dépôt GitHub. Les identifiants de campagnes, extensions `.csv`/`.npz`, noms de champs de métadonnées, inventaires de fichiers et mentions de points de contrôle ont été remplacés par des descriptions physiques ou des nombres de cas. Le lien GitHub et la licence MIT ne subsistent que dans les sections `Data availability`, comme autorisé. Le vocabulaire de révision, de contrôle qualité et de diagnostic « corrigé » a été reformulé en vocabulaire de publication (`dataset consistency checks`, `junction budget`, `field-data diagnostic`), sans retrait ni ajout de résultat physique. Les quatre PDF ont été recompilés deux fois : 19 p. (article propre), 22 p. (supplément propre), 21 p. (article annoté), 23 p. (supplément annoté), avec zéro référence indéfinie et aucun avertissement `Overfull`/`Underfull`. Le texte extrait des PDF ne contient aucune commande LaTeX brute ; les 30 légendes du supplément conservent leur ligne Alt text.

