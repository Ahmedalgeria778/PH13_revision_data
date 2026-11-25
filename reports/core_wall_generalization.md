# Additive core/wall budget: verification and qualified generalization

Input: `corrections for reviewer/04_additive_core_wall_budget/core_wall_budget.csv` (506 rows, 253 cases x 2 band widths).
Script: `corrections for reviewer/07_final_scientific_revision/analyze_core_wall.py`.

Integrity checks: 506 unique (n,Re,N,delta) rows, 253 unique cases, max |D_mask-(D_wall+D_core)| = 2.78e-17.

## Exact requested case: Re=1000, N=256, delta=0.05 L_c

| n | D/A_mask | wall/A_mask | core/A_mask | wall share | core share |
|---:|---:|---:|---:|---:|---:|
| 2 | 0.010289 | 0.008853 | 0.001437 | 86.0% | 14.0% |
| 3 | 0.008943 | 0.006941 | 0.002002 | 77.6% | 22.4% |
| 4 | 0.008797 | 0.006329 | 0.002468 | 71.9% | 28.1% |
| 6 | 0.008968 | 0.006235 | 0.002733 | 69.5% | 30.5% |
| 8 | 0.009199 | 0.006378 | 0.002821 | 69.3% | 30.7% |

Delta n=4 -> 8: D/A_mask 0.008797 -> 0.009199 (+0.000403, +4.58%); core/A_mask +0.000353 (87.76% of the rise), wall/A_mask +0.000049 (12.24%). The 88% figure is the **core fraction of the increase**, not the core share of D/A (which is 30.7% at n=8).

## Generalization (Re=100, 500, 1000; N=128/256; delta=0.025/0.05)

Definition used: `n_low` = sampled argmin of D/A_mask on the available n grid; `n_high` = largest available n (8 when present). `core_fraction = (core/A(n_high)-core/A(n_low))/(D/A(n_high)-D/A(n_low))`; core 'dominates' when this fraction > 50% and the total rise is positive.

| Re | N | delta/Lc | n grid | n_low | n_high | D/A rise | core rise | core fraction | dominant? |
|---:|---:|---:|---|---:|---:|---:|---:|---:|---|
| 100 | 128 | 0.025 | 1.25,1.5,1.75,2,2.5,3,4,5,6,8 | 3 | 8 | +0.007123 | +0.007044 | 98.9% | YES |
| 100 | 128 | 0.050 | 1.25,1.5,1.75,2,2.5,3,4,5,6,8 | 3 | 8 | +0.007123 | +0.005755 | 80.8% | YES |
| 500 | 128 | 0.025 | 1.25,1.5,1.75,2,2.5,3,4,5,6,8 | 4 | 8 | +0.000978 | +0.000876 | 89.6% | YES |
| 500 | 128 | 0.050 | 1.25,1.5,1.75,2,2.5,3,4,5,6,8 | 4 | 8 | +0.000978 | +0.000601 | 61.5% | YES |
| 1000 | 128 | 0.025 | 1.25,1.5,1.75,2,2.5,3,4,5,6,8 | 4 | 8 | +0.000404 | +0.000361 | 89.5% | YES |
| 1000 | 128 | 0.050 | 1.25,1.5,1.75,2,2.5,3,4,5,6,8 | 4 | 8 | +0.000404 | +0.000298 | 73.8% | YES |
| 100 | 256 | 0.025 | 2.5,3,4 | 3 | 4 | +0.000600 | +0.001273 | 212.2% | YES |
| 100 | 256 | 0.050 | 2.5,3,4 | 3 | 4 | +0.000600 | +0.001534 | 255.7% | YES |
| 500 | 256 | 0.025 | 1.25,1.5,1.75,2,2.25,2.5,2.75,3,3.25,3.5,3.75,4,4.25,4.5,5,6,8 | 3.75 | 8 | +0.001022 | +0.000996 | 97.4% | YES |
| 500 | 256 | 0.050 | 1.25,1.5,1.75,2,2.25,2.5,2.75,3,3.25,3.5,3.75,4,4.25,4.5,5,6,8 | 3.75 | 8 | +0.001022 | +0.000755 | 73.8% | YES |
| 1000 | 256 | 0.025 | 1.25,1.5,1.75,2,2.25,2.5,2.75,3,3.25,3.5,3.75,4,4.25,4.5,5,6,8 | 3.75 | 8 | +0.000410 | +0.000446 | 108.7% | YES |
| 1000 | 256 | 0.050 | 1.25,1.5,1.75,2,2.25,2.5,2.75,3,3.25,3.5,3.75,4,4.25,4.5,5,6,8 | 3.75 | 8 | +0.000410 | +0.000434 | 105.7% | YES |

### Fixed n=4 -> n=8 comparison (where both exponents exist)

| Re | N | delta/Lc | D/A rise | core rise | core fraction | dominant? |
|---:|---:|---:|---:|---:|---:|---|
| 100 | 128 | 0.025 | +0.006356 | +0.005841 | 91.9% | YES |
| 100 | 128 | 0.050 | +0.006356 | +0.004319 | 67.9% | YES |
| 500 | 128 | 0.025 | +0.000978 | +0.000876 | 89.6% | YES |
| 500 | 128 | 0.050 | +0.000978 | +0.000601 | 61.5% | YES |
| 1000 | 128 | 0.025 | +0.000404 | +0.000361 | 89.5% | YES |
| 1000 | 128 | 0.050 | +0.000404 | +0.000298 | 73.8% | YES |
| 100 | 256 | 0.025 | n/a (n=8 absent; grid 2.5,3,4) | n/a | n/a | n/a |
| 100 | 256 | 0.050 | n/a (n=8 absent; grid 2.5,3,4) | n/a | n/a | n/a |
| 500 | 256 | 0.025 | +0.000992 | +0.000921 | 92.9% | YES |
| 500 | 256 | 0.050 | +0.000992 | +0.000657 | 66.3% | YES |
| 1000 | 256 | 0.025 | +0.000403 | +0.000402 | 99.8% | YES |
| 1000 | 256 | 0.050 | +0.000403 | +0.000353 | 87.8% | YES |

### Caveats

1. The n grids are uneven. N=128 uses the 10-point reference grid {1.25,1.5,1.75,2,2.5,3,4,5,6,8}; N=256 uses 17 exponents at Re=300/500/1000 and only n={2.5,3,4} at Re=100. A 'sampled minimum' is therefore a property of that grid, not an optimized continuous minimum.
2. At Re=100, N=256, n=8 is absent; the only N=256 Re=100 exponents are 2.5, 3 and 4. No n=4->8 statement can be made there.
3. Absolute D/A levels are not grid-converged (e.g. Re=1000,n=4,delta=0.025: 0.007144 at N=128 vs 0.008797 at N=256), so every fraction above is a statement about the archived grids and the specified band width only.
4. The denominator is always A_mask, never A_core or the exact A(n). Wall/core shares change with delta; only the additive identity is delta-independent.
5. A 'core fraction of the rise' above 100% (e.g. Re=100,N=256 and Re=1000,N=256 in the sampled-min-to-max table) means the wall term decreases while the total rise stays positive. It is not a share of D/A and cannot exceed 100% in that sense.

## Outputs

* `core_target_Re1000_N256_d005.csv`, `core_target_delta_n4_to_n8.csv`, `core_generalization.csv`, `core_n4_to_n8.csv`.
