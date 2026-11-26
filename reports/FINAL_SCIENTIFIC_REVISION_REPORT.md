# PH13 final targeted scientific revision

Date: 2026-11-25
Python: `C:\Users\user\AppData\Local\Programs\Python\Python314\python.exe`
Output directory: `C:\Users\user\Documents\Default Project\GIRVD (revised)\corrections for reviewer\07_final_scientific_revision`
All source/data reads were read-only; all new files are in the output directory.

## Commands (run from the output directory)

```bat
C:\Users\user\AppData\Local\Programs\Python\Python314\python.exe verify_campaigns.py
C:\Users\user\AppData\Local\Programs\Python\Python314\python.exe analyze_core_wall.py
C:\Users\user\AppData\Local\Programs\Python\Python314\python.exe compute_lmov.py
C:\Users\user\AppData\Local\Programs\Python\Python314\python.exe audit_plid.py
```

---

## 1. Campaign counts

Authoritative counts are taken from archived `.npz` files, not from incomplete manifests. The campaign inventory uses the strict production-name regex `se_n<...>_Re<...>_N<...>(?:_ckpt)?.npz`; suffixed control files such as `*_proj.npz` are excluded there. The separate `P_lid` inventory counts every `.npz` and therefore finds 15 projected final fields in `data_lid_projected`.

| Dataset | Final fields | Distinct `(n,Re)` | N | Result |
|---|---:|---:|---|---|
| `05_dataset/data_all190` | 190 | 190 | 128 | 10 `n` x 19 `Re` (`100..1000` step 50). Claim **190 correct**. |
| `05_dataset/data_refine` | 50 | 50 | 128 | Archived campaign is **50 cases**, not 54. Re set has **8** values: `{300,325,350,500,850,875,900,1000}`; per-Re counts `6,9,6,7,6,9,6,1`. |
| `05_dataset/data_refine_seed` | 28 | 28 | 128 | Needed for the N128 comparison union. |
| `05_dataset/data_conv256` | 50 | 50 | 256 | 17 `n` values at `Re={300,500,1000}`; not a 17x3 cross product. |
| `05_dataset/data_conv256_lowRe` | 13 | 13 | 256 | Includes `Re={100,150,200,250}` and one extra `n=2.25, Re=300` case. |
| N256 total | **63** | 63 | 256 | 50 + 13; no duplicate `(n,Re)`. |

N128 union for comparison: `data_all190` + `data_refine` + `data_refine_seed` = **259** distinct pairs. Matched N256 cases: **62**; one unmatched case, `(n,Re)=(4.25,300)`, file `se_n4p25_Re300_N256.npz`. Internal `n/Re/N` metadata matched filenames in all checked fields: **0 mismatches**.

Manuscript implication: 190 and 50 are correct; “6 Re” describes the original `generate_local_refinement.py` plan, not the archived campaign; 63 N256 fields and 62 comparable cases are correct only when `data_conv256_lowRe` and `data_refine_seed` are included.

Details: `campaign_verification.md`, `campaign_inventory.csv`, `campaign_N256_matching.csv`, `campaign_refine_matrix.csv`.

---

## 2. Additive core/wall dissipation budget

Input: `corrections for reviewer/04_additive_core_wall_budget/core_wall_budget.csv` (506 rows = 253 cases x 2 band widths). Integrity: 506 unique `(n,Re,N,δ)` rows, 253 unique cases, max `|D_mask-(D_wall+D_core)| = 2.78e-17`.

Target case: `Re=1000, N=256, δ/L_c=0.05`.

| n | `D/A_mask` | `wall/A_mask` | `core/A_mask` | wall share | core share |
|---:|---:|---:|---:|---:|---:|
| 2 | 0.010289 | 0.008853 | 0.001437 | 86.0% | 14.0% |
| 3 | 0.008943 | 0.006941 | 0.002002 | 77.6% | 22.4% |
| 4 | 0.008797 | 0.006329 | 0.002468 | 71.9% | 28.1% |
| 6 | 0.008968 | 0.006235 | 0.002733 | 69.5% | 30.5% |
| 8 | 0.009199 | 0.006378 | 0.002821 | 69.3% | 30.7% |

`n=4 -> 8`: `D/A_mask` rises `0.008797 -> 0.009199` (+`0.000402`, +4.57%). Core rises +`0.000353`; wall rises +`0.000049`. Hence the core supplies **87.7597%** of the rise and the wall **12.2403%**. The “88%” statement is therefore the **core fraction of the increase**, not the core share of `D/A` (30.7% at `n=8`).

Qualified generalization (`Re=100,500,1000`; `N=128,256`; `δ/L_c=0.025,0.05`): for every fixed `n=4 -> 8` comparison where `n=8` exists, the core share of a positive `D/A` rise exceeds 50%, ranging from 61.5% to 99.8%. At `Re=100,N=256` only `n={2.5,3,4}` exists, so no `n=4->8` claim is possible. Sampled-minimum-to-maximum comparisons can exceed 100% when the wall term decreases; such values are not shares of `D/A`. Absolute `D/A` levels are resolution- and band-dependent.

Details: `core_wall_generalization.md`, `core_target_Re1000_N256_d005.csv`, `core_target_delta_n4_to_n8.csv`, `core_generalization.csv`, `core_n4_to_n8.csv`.

---

## 3. Moving-boundary arclength `L_mov`

The lid is the whole upper arc of `|x|^n+|y|^n=1` (`a=b=1`, `L_c=2`), as defined in `01_geometry/superellipse.py` lines 20–31 and manuscript lines 105–118. With `p=2/n`, first quadrant:

```text
x = cos^p(theta),  y = sin^p(theta),  0 <= theta <= pi/2
ds/dtheta = p*sqrt(cos^(2p-2) sin^2 + sin^(2p-2) cos^2)
L_mov = 2 * integral_0^(pi/2) ds/dtheta dtheta
```

For `n>2` the endpoint singularities are integrable. An independent Cartesian quadrature uses the regularising substitution `t=1-u^n`:

```text
L_quarter = n * integral_0^1 u^(n-1)
            sqrt(1 + (1-u^n)^(2n-2) (1-(1-u^n)^n)^(2/n-2)) du
```

mpmath working precision: 60 decimal digits. The Cartesian form is authoritative; for `n>=100` the trigonometric integrand has an endpoint layer too thin for default quadrature degree, while the Cartesian values agree with an independent dense-polyline check.

| n | `L_mov` | `L_mov/L_c` |
|---:|---:|---:|
| 1.25 | 2.8789718432635987957063 | 1.4394859216317993979 |
| 2 | 3.1415926535897932384626 | 1.5707963267948966192 |
| 4 | 3.5088489717820208235532 | 1.7544244858910104118 |
| 8 | 3.7389869262422749480672 | 1.8694934631211374740 |

Validation: `n=1 -> 2*sqrt(2)` and `n=2 -> pi` reproduced to ~1e-30; finite-`n` approaches to the square limit 4 are `3.9779688279` (`n=100`), `3.9977877972` (`n=1000`), `3.9997786888` (`n=10000`). This is a geometric limit only: the manuscript treats the square/Ghia cavity as a different forcing law.

Details: `l_mov_report.md`, `l_mov.csv`, `l_mov_validation.csv`.

---

## 4. Can archived LBM fields support a reliable `P_lid`?

**Verdict: no, not from final fields alone.** The production estimator is the MEM link sum

```text
P_lid = sum_links (e_q . u_wall) * (f_new[q] + f_post[opp])
```

It requires same-step populations and wall-link geometry. Archived final fields store `rho, ux, uy, fluid, X, Y` plus metadata, but no `f`, hence no `f_post` or `f_new`.

Inventory: **810** final `.npz` files under `05_dataset`, **0** with `f`; **148** checkpoint files, **148** with both `f` and `it`. Representative checkpoint pattern: `f|it`. Representative final pattern includes `rho|ux|uy|fluid|X|Y` and metadata only.

The only archived `P_lid` series was produced from checkpoints or fresh runs, not final fields:

| N | source | iteration | `P_lid` | `P/Phi` |
|---:|---|---:|---:|---:|
| 64 | `run` | 192900 | 3.484430e-04 | 4.268 |
| 128 | `run` | 364000 | 5.495369e-04 | 2.439 |
| 256 | `*_ckpt.npz` | 225000 | 1.000460e-03 | 1.778 |
| 512 | `*_ckpt.npz` | 475000 | 1.927010e-03 | 1.465 |

It increases with `N` and `P/Phi` is not unity; it must not be presented as a grid-converged or verified global power balance.

The alternative stress reconstruction from archived `(rho,u)` is not a substitute. The discrete identity test on `n=4, Re=1000, N=128` gives `int(div F)/(-int 2phi) = -4.418997647` (expected +1) and required pressure scale `-0.07827867175` (expected +1). The pressure convention `p=(rho-1)/(3 U_lid^2)` with `U_lid=0.05` is only post-processing; e.g. the representative final field `data_all190/se_n4p0_Re1000_N128.npz` has fluid-cell `rho` in `[1.08116, 1.0858]`.

Recommended manuscript scope: state that the lid-power estimate is compared only with the available link-level/pressure diagnostics and does **not** constitute verification of a global power–dissipation balance from archived macroscopic fields.

Details: `plid_audit_report.md`, `plid_npz_inventory.csv`, `plid_dataset_summary.csv`, `plid_source_facts.csv`, `plid_existing_estimates.csv`.

---

## 5. New artifacts

All paths below are relative to `C:\Users\user\Documents\Default Project\GIRVD (revised)`.

### Authoritative scripts

* `corrections for reviewer/07_final_scientific_revision/verify_campaigns.py`
* `corrections for reviewer/07_final_scientific_revision/analyze_core_wall.py`
* `corrections for reviewer/07_final_scientific_revision/compute_lmov.py`
* `corrections for reviewer/07_final_scientific_revision/audit_plid.py`

### Authoritative CSV/reports

* `corrections for reviewer/07_final_scientific_revision/FINAL_SCIENTIFIC_REVISION_REPORT.md`
* `corrections for reviewer/07_final_scientific_revision/campaign_verification.md`
* `corrections for reviewer/07_final_scientific_revision/campaign_inventory.csv`
* `corrections for reviewer/07_final_scientific_revision/campaign_N256_matching.csv`
* `corrections for reviewer/07_final_scientific_revision/campaign_refine_matrix.csv`
* `corrections for reviewer/07_final_scientific_revision/core_wall_generalization.md`
* `corrections for reviewer/07_final_scientific_revision/core_target_Re1000_N256_d005.csv`
* `corrections for reviewer/07_final_scientific_revision/core_target_delta_n4_to_n8.csv`
* `corrections for reviewer/07_final_scientific_revision/core_generalization.csv`
* `corrections for reviewer/07_final_scientific_revision/core_n4_to_n8.csv`
* `corrections for reviewer/07_final_scientific_revision/l_mov_report.md`
* `corrections for reviewer/07_final_scientific_revision/l_mov.csv`
* `corrections for reviewer/07_final_scientific_revision/l_mov_validation.csv`
* `corrections for reviewer/07_final_scientific_revision/plid_audit_report.md`
* `corrections for reviewer/07_final_scientific_revision/plid_npz_inventory.csv`
* `corrections for reviewer/07_final_scientific_revision/plid_dataset_summary.csv`
* `corrections for reviewer/07_final_scientific_revision/plid_source_facts.csv`
* `corrections for reviewer/07_final_scientific_revision/plid_existing_estimates.csv`

### Exploratory diagnostics retained for reproducibility

* `corrections for reviewer/07_final_scientific_revision/_explore.py`
* `corrections for reviewer/07_final_scientific_revision/_explore2.py`
* `corrections for reviewer/07_final_scientific_revision/_explore3.py`
* `corrections for reviewer/07_final_scientific_revision/_libs.py`
* `corrections for reviewer/07_final_scientific_revision/_inspect_budget.py`
* `corrections for reviewer/07_final_scientific_revision/_diag_lmov.py`
* `corrections for reviewer/07_final_scientific_revision/_diag2_lmov.py`
* `corrections for reviewer/07_final_scientific_revision/_diag3_lmov.py`

### Additional outputs from earlier work in this directory

* `corrections for reviewer/07_final_scientific_revision/common_support_fem_lbm.py`
* `corrections for reviewer/07_final_scientific_revision/common_support_dissipation.csv`
