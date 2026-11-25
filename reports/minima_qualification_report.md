# Qualification des minima et des seuils (donnees archivees)

Recipe: central differences on the gradient-valid fluid mask; A_mask = n_valid dx^2; D/A_mask uses the SAME support as D. Estimator: sampled argmin, then an ordinary-least-squares quadratic on either 3 points (argmin plus one neighbour on each side) or 5 points (two neighbours on each side). Non-finite values are excluded before fitting; the fitted vertex is accepted only if a>0 and it lies inside the support, otherwise argmin is retained and flagged.

## Sensibilite du fit : N=128 union, Re=300/500/1000

| Re | quantity | 3-pt n* | 5-pt n* | argmin | margin 3-pt % | margin 5-pt % |
|---:|---|---:|---:|---:|---:|---:|
| 300 | D_over_A_mask | 3.411 | 3.442 | 3.5 | 0.084 | 0.034 |
| 300 | D | 2.600 | 2.599 | 2.5 | 0.063 | 0.315 |
| 500 | D_over_A_mask | 3.538 | 3.624 | 3.5 | 0.183 | 0.147 |
| 500 | D | 2.680 | 2.598 | 2.75 | 0.236 | 0.164 |
| 1000 | D_over_A_mask | 4.065 | 4.471 | 4 | 1.190 | 1.323 |
| 1000 | D | 2.794 | 2.381 | 3 | 0.192 | -0.010 |

## Resolution sensitivity of n*_D (5-point fits where available)

| group | Re | n*_D (5-pt) | argmin D | n*_D/A (5-pt) | argmin D/A |
|---|---:|---:|---:|---:|---:|
| N128_union | 100 | 2.874 | 2.5 | 3.641 | 3 |
| N128_union | 300 | 2.599 | 2.5 | 3.442 | 3.5 |
| N128_union | 500 | 2.598 | 2.75 | 3.624 | 3.5 |
| N128_union | 1000 | 2.381 | 3 | 4.471 | 4 |
| N256_union | 100 | - | 2.5 | 3.340 | 3 |
| N256_union | 300 | 2.598 | 2.5 | 3.521 | 3.5 |
| N256_union | 500 | 2.623 | 2.5 | 3.685 | 3.75 |
| N256_union | 1000 | 2.670 | 2.5 | 3.995 | 3.75 |
| N384_HR | 300 | - | 4 | - | 4 |
| N384_HR | 1000 | 2.765 | 3 | 5.530 | 4 |
| N512_HR | 300 | - | 4 | - | 4 |
| N512_HR | 1000 | 2.533 | 3 | 5.544 | 4 |

## Crossing diagnostics (log-interpolated; descriptive only)

| group | quantity | n1/n2 | bracket | Re_c | ratios at bracket |
|---|---|---|---|---:|---|
| N128_all190 | D | 2.5/3 | [850, 900] | 893.0 | 0.9996 -> 1.0001 |
| N128_all190 | D_over_A_mask | 3/4 | [300, 350] | 338.2 | 0.9980 -> 1.0006 |
| N128_refine | D | 2.5/3 | -- | -- | 0.9915 -> 0.9998 |
| N128_refine | D_over_A_mask | 3/4 | [325, 875] | 348.8 | 0.9994 -> 1.0140 |
| N128_union | D | 2.5/3 | [875, 900] | 892.9 | 0.9998 -> 1.0001 |
| N128_union | D_over_A_mask | 3/4 | [325, 350] | 337.6 | 0.9994 -> 1.0006 |
| N256_conv | D | 2.5/3 | -- | -- | 0.9900 -> 0.9966 |
| N256_conv | D_over_A_mask | 3/4 | -- | -- | 1.0014 -> 1.0166 |
| N256_lowRe | D | 2.5/3 | -- | -- | 0.9848 -> 0.9891 |
| N256_lowRe | D_over_A_mask | 3/4 | -- | -- | 0.9848 -> 0.9989 |
| N256_union | D | 2.5/3 | -- | -- | 0.9848 -> 0.9966 |
| N256_union | D_over_A_mask | 3/4 | [250, 300] | 272.2 | 0.9989 -> 1.0014 |
| N384_HR | D | 2.5/3 | -- | -- | -- |
| N384_HR | D_over_A_mask | 3/4 | -- | -- | 1.0172 -> 1.0172 |
| N512_HR | D | 2.5/3 | -- | -- | -- |
| N512_HR | D_over_A_mask | 3/4 | -- | -- | 1.0182 -> 1.0182 |
| N384_extB | D | 2.5/3 | -- | -- | 0.9849 -> 0.9885 |
| N384_extB | D_over_A_mask | 3/4 | [200, 250] | 228.3 | 0.9983 -> 1.0013 |
| N512_extB | D | 2.5/3 | -- | -- | 0.9852 -> 0.9885 |
| N512_extB | D_over_A_mask | 3/4 | [150, 200] | 199.2 | 0.9963 -> 1.0001 |

Interpretation: fitted locations are compared only on matched grids; absolute D levels are resolution-sensitive. A crossing of two sampled values is a threshold crossing at the sampling resolution, not an onset or a resolution-independent threshold.
