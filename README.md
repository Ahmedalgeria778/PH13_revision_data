# PH13 revision data

**Repository:** <https://github.com/Ahmedalgeria778/PH13_revision_data>  
**Prepared:** 2026-11-25  
**Companion article:** *Geometry-induced reorganization of viscous dissipation in superelliptic lid-driven cavities* (PH13).

This repository contains the reproducible post-processing outputs, scripts, figures and reports produced for the final targeted scientific revision of PH13. **It deliberately contains no manuscript source (`.tex`), no compiled manuscript PDF, no `PH13_manuscript*`/`PH13_supplementary*` file, and no raw archived `.npz` fields.** The original supplementary document remains in the manuscript package; only its new results are documented here.

---

## 1. Scope and key conclusions

No new lattice Boltzmann (LBM) campaign was launched. All LBM results were recomputed from archived final fields; the only new flow solves are targeted Taylor–Hood P2/P1 finite-element (FEM) verification cases.

The locked numerical results are:

| Item | Result |
|---|---|
| Common-support LBM/FEM dissipation | `ε_D = 0.72–20.02%` on 9,488–15,168 masked nodes; `D_FEM^Ω / D_FEM^M = 1.63–2.06` |
| Dissipation convention | `D = 2ν ∫ S:S dA`, with `ν = 2/Re` in paper units; LBM velocities are lid-normalized by `U_lid = 0.05`, FEM uses `U_lid = 1` |
| Meaning of historical `rel. D error` | `|D_FD,lattice − D_exact,lattice| / D_exact,lattice`, i.e. a gradient-reconstruction diagnostic, not an LBM/FEM validation error |
| FEM mesh ladder | levels 4/5/6: 1,024/4,096/16,384 triangles and 4,771/18,755/74,371 velocity + pressure unknowns |
| Picard convergence | tolerance `1e-9`; 36/36 solves converged in 14–34 iterations |
| Junction convention | strict nodal test `y > 0`; left junction `y = +1.22e-16` moving, right junction `y = 0` fixed; no blending |
| Curvature | circle test gives `κ = 1.000000` and `f_sharp = 0`; 190 rows recomputed with `w = 0.05 L_c` and threshold `κ_w ≥ 2⟨|κ|⟩_Γ` |
| Core/wall budget | 506 rows; maximum additivity residual `2.78e-17`; for `Re=1000, N=256, δ=0.05L_c`, the core contributes `87.8%` of the `n=4→8` rise, not `87.8%` of absolute dissipation |
| Campaign counts | `data_all190`: 190 fields; `data_refine`: 50 fields at 8 Reynolds numbers; `N=256`: 63 fields, 62 matched to `N=128`; unmatched case `(n,Re)=(4.25,300)` |
| Moving-wall length | `L_mov(1.25)=2.8789718432636`, `L_mov(2)=π`, `L_mov(4)=3.5088489717820`, `L_mov(8)=3.7389869262423` |
| Lid power | **Not quoted as a verified quantity.** 810 final fields have no distribution functions `f`; 148 checkpoints have `f,it`; archived flux ratio is `-4.419` instead of `+1` |
| Energy statement | continuous identity, exact discrete LBM balance and archived-field diagnostic are kept distinct; no global energy closure is claimed |

Pressure convention used in the diagnostic: `p_LBM = c_s²(ρ_LBM − 1)` with `c_s² = 1/3`, and `p = (ρ − 1)/(3 U_lid²)` in paper units with `U_lid = 0.05`.

---

## 2. Directory layout

```text
README.md
reports/                   Reviewer matrix, audit notes and all validation reports
data/
  curvature/               Corrected and before/after curvature tables
  junction/                Junction budget and archived-field identity check
  fem/                     FEM dissipation, mesh refinement, gradient reconstruction
  core_wall/               Additive wall/core budget
  minima/                  Case metrics, fit diagnostics, crossing diagnostics
  manuscript_tables/       Observable summary CSV used to build tables
  final_revision/          All authoritative CSV outputs from the final revision
scripts/
  curvature/               Curvature correction
  junction/                Junction budget
  fem/                     FEM validation and report generation
  core_wall/               Additive budget
  minima/                  Minimum qualification
  manuscript_support/      Figure/table generation helpers
  final_revision/          Campaign, L_mov, P_lid, common-support and core/wall scripts
figures/                   All regenerated revision figures (PNG and PDF)
logs/                      Recorded FEM execution logs
```

The reports in `reports/` are the authoritative narrative records. In particular:

* `FINAL_SCIENTIFIC_REVISION_REPORT.md` — consolidated final revision;
* `campaign_verification.md` — campaign counts and matching;
* `core_wall_generalization.md` — wall/core partition and the qualified `87.8%` statement;
* `l_mov_report.md` — upper-half moving-wall arclength;
* `plid_audit_report.md` — why `P_lid` cannot be recovered from final fields;
* `REVIEWER_RESPONSE_MATRIX.md` and `AUDIT_NOTES.md` — final response status and retained limitations.

---

## 3. Reproduction

### Environment

The scripts were executed with Python 3.14 using:

```text
numpy, scipy, pandas, matplotlib, scikit-fem, mpmath
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
```

The produced CSV files are already deposited under `data/`, so the reports and figures can be inspected without rerunning any solver.

---

## 4. Important cautions

1. The `87.8%` core share is the fraction of the **`n=4→8 increase** in `D/A_mask`, not the absolute core fraction of `D/A_mask`. Across all available increments the core share is `61.5–99.8%`.
2. Richardson extrapolations are not used as quantitative convergence estimates; FEM mesh differences are reported only as mesh sensitivity.
3. The junction contribution is cutoff-dependent and the discrete junction assignment is a machine-precision-sensitive implementation detail, not a physical regularization length.
4. `P_lid` must not be inferred from archived macroscopic fields. The production MEM estimate requires same-step populations on moving-wall links, available only in checkpoints or fresh runs, and those estimates are not grid-converged.
5. No global energy-balance closure is claimed from the archived fields.

---

## 5. Provenance

All numerical values deposited here derive from read-only post-processing of the archived PH13 fields plus the targeted FEM solves recorded in `logs/`. The detailed referee reports for reviewers #4 and #5 are not available in the workspace, so literal compliance with those reports cannot be certified; the response is organized by issue in `reports/REVIEWER_RESPONSE_MATRIX.md`.
