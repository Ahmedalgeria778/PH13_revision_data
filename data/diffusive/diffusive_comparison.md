# Diffusive-scaling check for n=4, Re=1000

U_lid(N) = 0.05*128/N; nu_lbm and tau are kept nearly fixed while the
lattice Mach number decreases as 1/N. All D values use the same
gradient-valid quadrature and physical junction radii.

| N | U_lid | tau | D_prod(r0=0) | D_diff(r0=0) | D_prod(r0=0.5) | D_diff(r0=0.5) |
|---|---|---|---|---|---|---|
| 128 | 0.050000 | 0.519050 | 0.025590 | 0.025590 | 0.015117 | 0.015117 |
| 256 | 0.025000 | 0.519125 | 0.032090 | 0.032623 | 0.017179 | 0.017176 |
| 384 | 0.016667 | 0.519150 | 0.035407 | 0.036158 | 0.017864 | 0.017859 |
| 512 | 0.012500 | 0.519162 | 0.037509 | 0.038374 | 0.018184 | 0.018179 |

## Increment diagnostics

- r0=0: production increments 0.006500, 0.003317, 0.002102; diffusive increments 0.007033, 0.003535, 0.002216 (128→256, 256→384, 384→512).
  Equal-doubling order from 128/256/512: production 0.26; diffusive 0.29.
  128/256/384 fitted order: production 0.25; diffusive 0.27.
- r0=0.25: production increments 0.002979, 0.001008, 0.000467; diffusive increments 0.002972, 0.001007, 0.000466 (128→256, 256→384, 384→512).
  Equal-doubling order from 128/256/512: production 1.01; diffusive 1.01.
  128/256/384 fitted order: production 0.97; diffusive 0.97.
- r0=0.5: production increments 0.002062, 0.000685, 0.000321; diffusive increments 0.002059, 0.000683, 0.000319 (128→256, 256→384, 384→512).
  Equal-doubling order from 128/256/512: production 1.04; diffusive 1.04.
  128/256/384 fitted order: production 1.01; diffusive 1.01.

The N=128 fields agree by construction because U_lid and tau match.
The comparison tests only whether lowering the lattice Mach number
changes the remaining drift; it is not a continuum certification.
