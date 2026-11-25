# Upper-half moving-wall arclength L_mov

Script: `corrections for reviewer/07_final_scientific_revision/compute_lmov.py`.
mpmath working precision: 60 decimal digits.

The moving lid is the whole upper arc of `|x|^n+|y|^n=1` (a=b=1, L_c=2), as
defined in `01_geometry/superellipse.py` lines 20-31 and manuscript lines 105-118.
With `p=2/n`, the first-quadrant parametrisation is `x=cos^p(theta)`,
`y=sin^p(theta)`, and `L_mov=2*integral_0^(pi/2) p*sqrt(cos^(2p-2)sin^2 + sin^(2p-2)cos^2) dtheta`.
For n>2 the integrand has integrable algebraic endpoint singularities; the
quadrature splits at theta=pi/4. An independent Cartesian quadrature uses
the substitution t=1-u^n to remove the endpoint singularity at t=1. The Cartesian
form is used as the authoritative value: for n>=100 the trigonometric integrand
has an endpoint layer too thin for the default mpmath quadrature degree, whereas
the Cartesian values agree with an independent dense polyline check.

## Requested values

| n | L_mov (mpmath, trig) | L_mov (mpmath, Cartesian, authoritative) | L_mov/L_c |
|---:|---:|---:|---:|
| 1.25 | 2.8789718432635987957063 | 2.8789718432635987957063 | 1.4394859216317993979 |
| 2 | 3.1415926535897932384626 | 3.1415926535897932384626 | 1.5707963267948966192 |
| 4 | 3.5088489717820208235532 | 3.5088489717820208235532 | 1.7544244858910104118 |
| 8 | 3.7389869262422738271175 | 3.7389869262422749480672 | 1.869493463121137474 |

For n=1.25, 2, 4 and 8 the two independent high-precision quadratures agree to
at least the digits shown in `l_mov.csv`.

## Known-limit validation

| case | n | computed L_mov | reference | abs error | note |
|---|---:|---:|---:|---:|---|
| diamond: two straight segments | 1 | 2.8284271247461900976033 | 2.8284271247461900976033 | 6.038428607e-31 | exact |
| circle radius 1: upper semicircle | 2 | 3.1415926535897932384626 | 3.1415926535897932384626 | 4.971158028e-31 | exact |
| square limit n->infinity (finite-n value at n=100) | 100 | 3.9779688279152625781286 | 4.0 | 0.02203117208 | finite n |
| square limit n->infinity (finite-n value at n=1000) | 1000 | 3.9977877971889462271712 | 4.0 | 0.002212202811 | finite n |
| square limit n->infinity (finite-n value at n=10000) | 10000 | 3.9997786887847870572181 | 4.0 | 0.0002213112152 | finite n |

The `n=100`, `n=1000` and `n=10000` rows are finite-n approaches to the
square limit 4, not assertions that the square cavity has the same lid law:
the manuscript explicitly treats the square/Ghia case as a different forcing.

## Outputs

* `l_mov.csv`, `l_mov_validation.csv`.
