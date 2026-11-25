# Findings from the wider `C:\Users\user\Documents` scan

Read-only scan of `C:\Users\user\Documents`, excluding `GIRVD (revised)` and
`travail pc taki_final`, performed for the user's final instruction. Only
findings that are concrete and traceable are recorded here; none is copied into
the manuscript without an executed regeneration or a direct CSV/JSON check.

## Directly useful and consistent with the revision

| Source | What it gives | How it is used |
|---|---|---|
| `Qoder\2026-11-10\21bb4dee\PoF_superellipse_dissipation_study\08_operator_results\REFERENTIEL_PH13.md` | Defines `reference-190` as the authoritative frozen dataset and records the audit referential. | Provenance cross-check for the archived campaigns; supports the statement that all post-processing uses `reference-190`. |
| `...\08_operator_results\PH13_manuscript\PH13_manuscript_revised.pdf` and `PH13_supplementary_revised.pdf` (2026-11-21) | The V4 52-page text and its supplement. | Confirms which claims had to be withdrawn; no number from these PDFs is reused without CSV verification. |
| `...\06_physics\results_puissance\diag_bilan_identite.md` / `.csv` | `W_paroi/A ≈ 1` is an identity check, while `P_MEM/A = 0.8454` and `Φ/A = 0.4756` are estimator diagnostics. | Reinforces the retained limitation that no global power/dissipation closure is certified; consistent with `identity_check.csv` (`-4.419` instead of `+1`). |
| `...\06_physics\results_puissance\diag_equation_bilan.md` / `.csv` | `P/Φ(k)` rises `2.36→3.15` (`N=256`) and `1.47→2.32` (`N=512`) as wall layers are removed. | Supports the wording that wall removal changes the estimated balance; not used as a physical dissipation value. |
| `...\06_physics\BILAN_RESERVES.md` | `P_MEM/P_traction = 0.9964` outside junctions but `P_MEM/Φ_complet = 1.3125` on the full domain. | Confirms that the junction excision is responsible for part of the imbalance; quoted only as a caveat. |
| `...\06_physics\results_canonique_ghia\canonique_ghia_Re1000.md` / `.json` | Independent Ghia Re=1000 run: `N=256`, residual `9.986835e-10`, V2 `ε=98.900%`, V3 `ε=17.527%`. | Supports the benchmark statement under the *Ghia* lid law only; explicitly separate from the present tangential-lid family. |
| `...\06_physics\results_conv18pts_revision\table_18pts.csv` / `synthese.json` | 18 matched convergence ladders. | Cross-check for the resolution-ladder campaign row and for the qualified convergence language. |
| `Default Project\superellipse_ondulation_aspect_ratio\results\audit\n384_status.json` / `n384_table.md` | Primary contrasts stable to `<1%` from `N=256→384`; balance residual about `2%`. | Used only to justify keeping "no grid-independent claim"; this is a different aspect-ratio study. |
| `Default Project\superellipse_ondulation_interaction\...\docs\12_mach_et_derive_contraste.md` | Mach number is not responsible for the `N=384→768` drift; an earlier `+19%` was a non-converged checkpoint. | Cross-check that the present `Ma=0.0866` fixed-Mach setting does not explain the dissipation drift. |
| `...\08_operator_results\PH13_pof_revision_derived\PH13_physical_regime_synthesis.json` | Per-case minima; at `Re=1000`, `n=4`, `D/A=0.00690091`. | Cross-check only: this value uses the exact area `A(n)`, while the manuscript uses the quadrature support `A_{\rm mask}` (`0.00714371` for the same case in `case_metrics.csv`). The two denominators must not be mixed. |
| `Qoder\2026-11-10\21bb4dee\backup_tex_avant_L\supp_GIRVD.tex` | Older square-cavity diagnostic: junction disks carry `65.1%` (`Re=100`) and `52.0%` (`Re=1000`) of the restored dissipation; `P_MEM/P_tr` agreement improves when the disks are excluded. | Corroborative caveat for the junction section; older backup, so no number is quoted in the manuscript without the present `junction_budget.csv` recomputation. |

## Explicitly NOT used

* `...\08_operator_results\PH13_pof_revision_derived\PH13_nearwall_curvature_analysis.{json,csv}`:
  these files contain the **defective** arclength interpolation (`κ_w,max=29.87`
  for the unit circle, `30.6` at `n=1.25`). Their pooled correlations (`0.907`,
  `0.801`, etc.) and the old near-wall share trend must not be quoted. The
  corrected values are in `01_curvature_validation/curvature_corrected_190.csv`.
* `PH13_manuscript_revised.tex` and its backups: old crossing claims (`Re_c≈338`
  with exact area, `≈893`) are retained only as history; the qualified numbers
  in `05_minima_qualification/crossing_diagnostics.csv` are used instead.
* Aspect-ratio and undulation-interaction papers: separate studies with similar
  geometry; their contrast and energy-closure numbers are not PH13 results and
  are not inserted into this manuscript.
* `PH13_final\PH13_interpretation.md`, `PH13_cost_curve.json`,
  `A_B0_B1_final_comparison.md`, `physics_observables.csv` and all operator
  metrics (`R²=0.97542`, `L_div=0.006183`, etc.): reserved for the separate
  DeepONet paper; deliberately absent from the physics-only manuscript.
* Older `paper_pof*` archives, `data_suivi` mirrors and unrelated top-level
  files: provenance/duplicates only; no unique result used.
