# Fixed-physical-wall-support dissipation, n=4, Re=1000

D_core(delta) = 2 nu sum_{M cap {dist>delta}} S:S dx^2, with dist the
distance to the exact superellipse boundary (n=4, a=b=1, L_c=2).
delta = 0.05 L_c = 0.10 and 0.10 L_c = 0.20. The boundary is sampled
with 300000 points and queried with a KD tree in physical
coordinates; the distance does not depend on the lattice spacing.

| N | D_M | D_core(0.05 L_c) | D_core(0.10 L_c) | D_wall(0.05 L_c) | D_wall(0.10 L_c) | D_r0=0.5 |
|---|---|---|---|---|---|---|
| 128 | 0.025590 | 0.008958 | 0.002817 | 0.016632 | 0.022772 | 0.015117 |
| 256 | 0.032090 | 0.008796 | 0.002675 | 0.023294 | 0.029415 | 0.017179 |
| 384 | 0.035407 | 0.008674 | 0.002645 | 0.026733 | 0.032763 | 0.017864 |
| 512 | 0.037509 | 0.008714 | 0.002641 | 0.028794 | 0.034868 | 0.018184 |

## Orders and resolution sensitivity

| quantity | fit 128/256/384 | fit 128/256/512 | equal-doubling 128/256/512 | |D_128-D_512|/|D_512| |
|---|---|---|---|---|
| $D_{r_0=0.5}$ | 1.01 | 0.33 | 1.04 | 16.9% |
| $D_{\rm core}(0.05L_c)$ | n/a | n/a | n/a | 2.8% |
| $D_{\rm core}(0.10L_c)$ | n/a | n/a | n/a | 6.7% |

The fixed-support core values are nearly flat and decrease slightly;
no positive fitted order is obtained from successive increments.
D_core + D_wall = D_M is exact by construction. Orders and relative
changes are diagnostics on archived grids, not continuum certifications.
