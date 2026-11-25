# Final reviewer-response matrix (2026-11-25)

The full original referee reports were not present in the shared workspace. The recalled questions in the formal letter therefore follow the reviewer-specific issue identifiers and the audit matrix retained in the revision record. The scientific responses and revision actions are final.

Formal letter: `RESPONSE_LETTER_FINAL.tex` / `RESPONSE_LETTER_FINAL.pdf`.

A separate report for Reviewer 3 was not supplied. The issue tagged `#3.3` in the internal audit trail was addressed together with Reviewer 4, Question 2.

## 1. Per-referee response structure

| Referee | Question | Topic | Final response summary | Location |
|---|---:|---|---|---|
| 1 | 1 | Wall-curvature circle test | Full periodic arclength interpolation and wrapped angle difference; unit circle gives `κ_max = κ_rms = 1.000000` and `f_sharp = 0`; all 190 rows recomputed. Curvature alone does not locate the `D/A` minimum. | Letter R1-Q1; Main §5; Suppl. S5 |
| 1 | 2 | Minima and corner counts | Sampled extrema and fit windows are qualified; corner counts are `1%` detection-threshold crossing brackets, not topological transitions. | Letter R1-Q2; Main §§5–6; Suppl. S12–S14 |
| 1 | 3 | Wall/core interpretation | The `87.8%` value is the core share of the `n=4→8` rise, not the absolute core share; wall-only claim withdrawn. | Letter R1-Q3; Main §5; Suppl. S6 |
| 2 | 1 | Square-limit boundary law | `n→∞` gives a square with piecewise tangential wall motion, not the Ghia cavity; projected lid is a kinematic definition only. | Letter R2-Q1; Main §§2,6; Suppl. S15 |
| 2 | 2 (`#2.4`) | Junction regularization and energy | No regularization length; junction dissipation is cutoff-dependent; archived-field flux ratio `-4.419` instead of `+1`; no global closure claimed. | Letter R2-Q2; Main §§5–6; Suppl. S8–S9 |
| 2 | 3 | Normalization and factor of two | LBM uses `U_lid=0.05`, FEM `U_lid=1`, both with `ν=2/Re` and `D=2ν∫S:S`; old `rel. D error` is a gradient-reconstruction diagnostic. | Letter R2-Q3; Main §§2,6; Suppl. S7 |
| 4 | 1 (`#4.B1`) | Square-limit statement | Misleading asymptotic claim removed; Introduction now defines the exponent-shape family exactly as requested. | Letter R4-Q1; Main §§2,6; Introduction |
| 4 | 2 (`#4.3`) | FEM gradients and dissipation | `D_FEM^Ω=2ν∫S:S` on P2/P1 mesh ladder; 36/36 solves at `1e-9` in 14–34 iterations; common-support `ε_D=0.72–20.02%` and `D_Ω/D_M=1.63–2.06`. | Letter R4-Q2; Main §6; Suppl. S7–S8 |
| 4 | 3 (`#4.4`) | Junction convention | Strict `y>0`; left junction `y=+1.22e-16` moving, right `y=0` fixed; no blending or smoothing. | Letter R4-Q3; Main §5; Suppl. S8 |
| 4 | 4 (`#4.3`) | Wall/core budget | Additive on common `A_mask`; max residual `2.78e-17` over 506 rows; rise beyond the trough is core-driven but band- and resolution-dependent. | Letter R4-Q4; Main §§3–5; Suppl. S6 |
| 4 | 5 | Fit supports and crossings | Supports, exclusions and estimator moved to Supplement S12; no resolution-independent optimum or extrapolated threshold claimed. | Letter R4-Q5; Main §6; Suppl. S12 |
| 5 | 1 (`#5.3`) | Additive wall/core budget | Same-denominator identity; `87.8%` is a rise fraction; absolute endpoint core shares `28.1%` and `30.7%`; increment range `61.5–99.8%`. | Letter R5-Q1; Main §§3–5; Suppl. S6 |
| 5 | 2 | Campaign inventory | `data_all190` = 190; `data_refine` = 50 at 8 `Re`; `N=256` = 63 fields, 62 matched; unmatched `(n,Re)=(4.25,300)`. | Letter R5-Q2; Main §6; Suppl. S11 |
| 5 | 3 | Lid power | `P_lid` not quoted: 810 final fields have no `f`; 148 checkpoints have `f,it`; flux ratio `-4.419`; `P/Φ` varies `4.268→1.465` with `N`. | Letter R5-Q3; Main §§5–6; Suppl. S9–S10 |
| 6 | 1 | Data availability | Repository contains final supplement, scripts, figures, tables, reports, README and MIT `LICENSE`; no main source/PDF and no raw `.npz`. | Letter R6-Q1; Data availability; repository |
| 6 | 2 | Structure and figures | Main reduced to 7 physics-only sections; supplement is one coherent S1–S15 document; Figure 2 legend/ticks, field plate and near-wall/curvature axes enlarged. | Letter R6-Q2; Main 19 pp.; Suppl. 22 pp. |
| 6 | 3 | Explicit limitations | No global energy closure, no verified `P_lid`, no absolute `N=128` convergence, no universal optimum, no topological inference. | Letter R6-Q3; Main §6; Abstract and Conclusions |
| 3 | — | No supplied report | No point-by-point response possible; `#3.3` covered under Reviewer 4 Question 2. | Letter R3 note |

## 2. Final document state

* Main article: `PH13_manuscript_physics_only.tex/pdf`, 19 pages, seven numbered sections, no undefined references.
* Supplement: `PH13_supplementary_final.tex/pdf`, 22 pages, single part, sections S1--S15, no undefined references.
* Repository: <https://github.com/Ahmedalgeria778/PH13_revision_data>, with English MIT `LICENSE`.
* Installed package: `08_operator_results/PH13_manuscript/`, with previous deliverables in `backup_pre_publish_2026-11-25/`.

## 3. Withdrawn formulations

* ``the drift is not a resolution artefact'' → fitted locations similar on matched grids, absolute levels unresolved.
* ``the wall layer sets its location'' → shallow minimum is a wall/core compensation.
* ``total momentum content'' → integrated kinetic energy.
* ``resolution-independent to about 2%'' → resolution-sensitive shallow optimum.
* ``onset'' / ``topologically distinct'' → `1%` detection-threshold crossing bracket.
* ``classical square cavity recovered asymptotically'' → square limit with piecewise tangential wall motion.

## 4. Retained limitations

* No global energy-balance closure from archived macroscopic fields.
* No absolute dissipation value at `N=128` presented as converged.
* No universal or resolution-independent minimum.
* No verified `P_lid`.
* No topological inference from a sub-percent crossing.
* No literal compliance certification for referee reports that were not supplied.
