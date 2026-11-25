# PH13 revision data

**Repository:** <https://github.com/Ahmedalgeria778/PH13_revision_data>  
**Prepared:** 2026-11-25  
**Companion article:** *Geometry-induced reorganization of viscous dissipation in superelliptic lid-driven cavities* (PH13).

This repository contains the reproducible post-processing outputs, scripts, figures, result tables, reports and the **final single-part supplementary document** for PH13. The main article source and compiled main-article PDF are **not** included. Raw archived `.npz` fields are **not** included because of their size.

## Copyright and license

Copyright (c) 2026 BENIAICHE Ahmed. All files in this repository are provided under the **MIT License**. See [`LICENSE`](LICENSE) for the full English license text and conditions.

---

## 1. Scope and key conclusions

No new lattice Boltzmann (LBM) campaign was launched. All LBM results were recomputed from archived final fields; the only new flow solves are targeted Taylor–Hood P2/P1 finite-element (FEM) verification cases.

| Item | Result |
|---|---|
| Common-support LBM/FEM dissipation | `ε_D = 0.72–20.02%` on 9,488–15,168 masked nodes; `D_FEM^Ω / D_FEM^M = 1.63–2.06` |
| Dissipation convention | `D = 2ν ∫ S:S dA`, with `ν = 2/Re` in paper units; LBM velocities are lid-normalized by `U_lid = 0.05`, FEM uses `U_lid = 1` |
| Meaning of the gradient-reconstruction column | `|D_FD,lattice − D_exact,lattice| / D_exact,lattice`, a gradient-reconstruction diagnostic, not an LBM/FEM validation error |
| FEM mesh ladder | levels 4/5/6: 1,024/4,096/16,384 triangles and 4,771/18,755/74,371 velocity + pressure unknowns |
| Picard convergence | tolerance `1e-9`; 36/36 solves converged in 14–34 iterations |
| Junction convention | strict nodal test `y > 0`; left junction `y = +1.22e-16` moving, right junction `y = 0` fixed; no blending |
| Curvature | unit-circle test gives `κ = 1.000000` and `f_sharp = 0`; 190 rows recomputed with `w = 0.05 L_c` and threshold `κ_w ≥ 2⟨|κ|⟩_Γ` |
| Core/wall budget | 506 rows; maximum additivity residual `2.78e-17`; for `Re=1000, N=256, δ=0.05L_c`, the core contributes `87.8%` of the `n=4→8` rise, not `87.8%` of absolute dissipation |
| Campaign counts | `data_all190`: 190 fields; `data_refine`: 50 fields at 8 Reynolds numbers; `N=256`: 63 fields, 62 matched to `N=128`; unmatched case `(n,Re)=(4.25,300)` |
| Moving-wall length | `L_mov(1.25)=2.8789718432636`, `L_mov(2)=π`, `L_mov(4)=3.5088489717820`, `L_mov(8)=3.7389869262423` |
| Lid power | **Not quoted as a verified quantity.** 810 final fields have no distribution functions `f`; 148 checkpoints have `f,it`; the archived flux ratio is `-4.419` instead of `+1` |
| Energy statement | continuous identity, exact discrete LBM balance and archived-field diagnostic are kept distinct; no global energy closure is claimed |

Pressure convention used in the diagnostic: `p_LBM = c_s²(ρ_LBM − 1)` with `c_s² = 1/3`, and `p = (ρ − 1)/(3 U_lid²)` in paper units with `U_lid = 0.05`.

---

## 2. Final supplement

The publication-ready supplement is a **single coherent document**:

* `supplement/PH13_supplementary_final.tex`
* `supplement/PH13_supplementary_final.pdf`
* `supplement/supp_*.tex` — external table fragments required to compile the supplement
* `supplement/Marked-Up_Supplementary.tex` / `.pdf` — marked-up version against the
  25 September 2026 supplementary submission (blue = new/revised, red appendix = removed)

It contains only supporting fluid-physics material: solver verification, database quality control, observable definitions, the reference-field atlas, wall-curvature diagnostics, the additive wall/core budget, common-support LBM/FEM dissipation, FEM mesh and junction conventions, energy and pressure conventions, moving-wall geometry, campaign inventory, fit diagnostics, corner-eddy analysis, and the projected-lid boundary-law convention. It contains no addendum, no revision history, no operator-learning material and no training/provenance discussion.

The supplement figures are in `figures/final_supplement/`; the final article figures `curve_dissipation_vs_n.png`, `map_dissipation.png`, `fig_fields_plate.png`, `fig_curvature.png` and `fig_nearwall_large_axes.png` are in `figures/`. The journal highlight image is supplied as `figures/Highlight_Image.tif` and `figures/Highlight_Image.jpeg` (2404 x 1882 px, 300 dpi).

Accessibility alt text for every figure and table is in `reports/Alt_Text.txt`; the Supplementary Online Material PDF also prints the alt text beneath each caption.

---

## 3. Directory layout

```text
README.md
LICENSE                    MIT license and copyright notice
supplement/                Final single-part supplement source, PDF and table fragments
reports/                   Reviewer responses, audit notes, validation reports and Alt_Text.txt
data/
  curvature/               Corrected and before/after curvature tables
  junction/                Junction budget and archived-field identity check
  fem/                     FEM dissipation, mesh refinement, gradient reconstruction
  core_wall/               Additive wall/core budget
  minima/                  Case metrics, fit diagnostics, crossing diagnostics
  manuscript_tables/       Observable summary CSV used to build tables
  final_revision/          Authoritative CSV outputs from the final revision
  final_supplement/        Source tables for the final figures and corner diagnostics
scripts/
  curvature/               Curvature correction
  junction/                Junction budget
  fem/                     FEM validation and report generation
  core_wall/               Additive budget
  minima/                  Minimum qualification
  corner/                  Corner-eddy post-processing
  manuscript_support/      Final figure/table generation helpers
  final_revision/          Campaign, L_mov, P_lid, common-support and core/wall scripts
figures/                   Final article figures, highlight image and figures used by the supplement
  final_supplement/        Supplemental figures at final publication resolution
logs/                      Recorded FEM execution logs
```

The reports in `reports/` are the authoritative narrative records. In particular:

* `FINAL_SCIENTIFIC_REVISION_REPORT.md` — consolidated final revision;
* `campaign_verification.md` — campaign counts and matching;
* `core_wall_generalization.md` — wall/core partition and the qualified `87.8%` statement;
* `l_mov_report.md` — upper-half moving-wall arclength;
* `plid_audit_report.md` — why `P_lid` cannot be recovered from final fields;
* `RESPONSE_LETTER_FINAL.tex/pdf/md/html` — formal English point-by-point response letter in the Physics of Fluids template style, with recalled questions in dark blue italics and responses in black;
* `REVIEWER_RESPONSE_MATRIX.md` and `AUDIT_NOTES.md` — point-by-point responses and retained limitations.

---

## 4. Reproduction

### Environment

The scripts were executed with Python 3.14 using:

```text
numpy, scipy, pandas, matplotlib, scikit-fem, mpmath, Pillow
```

The original archived `.npz` fields are **not** included here because of their size. To rerun the field-based scripts, place the original archive tree locally and adjust the archive paths at the top of the relevant scripts. The FEM scripts additionally require `scikit-fem`; the `L_mov` script uses `mpmath`.

### Principal commands

From `scripts/final_revision/`:

```bat
python verify_campaigns.py
python analyze_core_wall.py
python compute_lmov.py
python audit_plid.py
python common_support_fem_lbm.py
```

From the other script folders:

```bat
python scripts/curvature/curvature_fixed.py
python scripts/junction/junction_budget.py
python scripts/fem/fem_dissipation_validation.py
python scripts/fem/fem_gradient_reconstruction.py
python scripts/core_wall/core_wall_budget.py
python scripts/minima/minima_qualification.py
python scripts/corner/postprocess_corner.py
python scripts/corner/etude_corner_bnd.py
python scripts/manuscript_support/make_review_figures.py
```

The produced CSV files are already deposited under `data/`, so the reports and figures can be inspected without rerunning any solver. The supplement can be compiled with `pdflatex` from `supplement/` after placing its table fragments in the same directory.

---

## 5. Important cautions

1. The `87.8%` core share is the fraction of the **`n=4→8 increase** in `D/A_mask`, not the absolute core fraction of `D/A_mask`. Across all available increments the core share is `61.5–99.8%`.
2. Richardson extrapolations are diagnostics only and are not used as quantitative convergence estimates; FEM mesh differences are reported only as mesh sensitivity.
3. The junction contribution is cutoff-dependent and the discrete junction assignment is a machine-precision-sensitive implementation detail, not a physical regularization length.
4. `P_lid` must not be inferred from archived macroscopic fields. The production MEM estimate requires same-step populations on moving-wall links, available only in checkpoints or fresh runs, and those estimates are not grid-converged.
5. No global energy-balance closure is claimed from the archived fields.
6. Projected-lid material is a kinematic boundary-law definition only; no converged projected-lid fields were generated for this article and no hydrodynamic sensitivity is inferred.

---

## 6. Provenance and reviewer responses

All numerical values deposited here derive from read-only post-processing of the archived PH13 fields plus the targeted FEM solves recorded in `logs/`. The point-by-point response is maintained in `reports/REVIEWER_RESPONSE_MATRIX.md`, with the supporting audit trail in `reports/AUDIT_NOTES.md`. Detailed reports were supplied for reviewers 1, 2, 4, 5 and 6; no separate report for reviewer 3 was supplied, and this gap is retained explicitly in the response.
