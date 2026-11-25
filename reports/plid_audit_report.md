# Can archived fields support a reliable P_lid?

Script: `corrections for reviewer/07_final_scientific_revision/audit_plid.py`.

## Verdict

**No, not from the archived final fields alone.** A reliable production `P_lid` is the
MEM link-sum `(e_q·u_wall)(f_new[q]+f_post[o])`. Final fields store only
`rho, ux, uy, fluid, X, Y` plus metadata: no `f`, hence no `f_post`, no `f_new`, and
no same-step boundary populations. `P_lid` can be computed only by instrumenting the
solver, using a checkpoint that contains `f,it`, or re-running the case.

Inventory: 810 final `.npz` files under `05_dataset`, of which 0
contain `f`; 148 checkpoint files, of which 148 contain both `f` and `it`.
Per-dataset counts and exact key patterns are in `plid_dataset_summary.csv`; the full
file-by-file inventory is in `plid_npz_inventory.csv`.

## Source-level evidence

* `06_physics/analyse_etape4_puissance.py` lines 15-17: P_lid = sum_links (e_q . u_wall) * (f_new[q] + f_post[opp]); requires f_post and f_new on moving-wall links.
* `06_physics/analyse_etape4_puissance.py` lines 26-28: Production script states that final .npz fields do not store f; N=256/512 use checkpoints, N=64/128 are re-run.
* `06_physics/analyse_etape4_puissance.py` lines 148-157: get_f(N) reads z['f'] and z['it'] from *_ckpt.npz, otherwise runs CurvedLBM from scratch.
* `06_physics/analyse_etape4_puissance.py` lines 170-172: rho,ux,uy = macroscopic(f); f_post = collide(f,S,fluid); stream_force(f_post,la,rho) yields P_lid.
* `02_LBM/mrt_collision.py` lines 64-69: rho = f.sum(axis=0), ux = sum(e_x f)/rho, uy = sum(e_y f)/rho; p=(rho-1)/(3 U_lid^2) is in physics_observables.py:327.
* `06_neural_operator/physics_observables.py` lines 325-337: Alternative post-processing reconstructs du_t/dn and pressure-strain from archived (rho,u); this is an estimate, not MEM.
* `corrections for reviewer/02_junction_energy_budget/junction_budget_report.md` lines 60-70: On n=4, Re=1000, N=128: int(div F)/(-int 2phi) = -4.419 (expected +1); required pressure scale = -0.0783 (expected +1). Archived (rho,u) do not satisfy the discrete identity.

## Representative archived final field (rho convention)

`05_dataset/data_all190/se_n4p0_Re1000_N128.npz`: n=4, Re=1000, N=128,
14868 fluid cells. On fluid cells: rho in
[1.08116, 1.0858], mean 1.08296;
with `U_lid=0.05`, `p=(rho-1)/(3U_lid^2)` spans
[10.8218, 11.44].
This pressure is only a post-processing convention applied to an archived rho field;
it does not restore the populations needed by MEM.

## Why the stress-based reconstruction is not a substitute

`physics_observables.py:325` computes `lid_power = 2*nu*sum(du_t/dn ds)` from the
near-wall velocity, and lines 326-337 compute pressure-strain forces from `p` and `S`.
Both use archived time-averaged macroscopic fields and a sampled wall location. The
independent discrete identity test on `n=4, Re=1000, N=128` gives:
`int(div F)/(-int 2phi)` = `-4.418997647` (expected +1) and required pressure scale
`-0.07827867175` (expected +1). Therefore the flux built from
archived `(rho,u)` is not a verified energy balance, and it cannot be used to claim
that `P_lid=D`.

## Existing P_lid numbers and their provenance

The only archived `P_lid` series (`06_physics/results_puissance/etape4_puissance.csv`)
was produced from `f` in checkpoints or from fresh runs, not from final fields:

| N | source_f | it | P_lid | P/Phi |
|---:|---|---:|---:|---:|
| 64 | run | 192900 | 3.484430e-04 | 4.268 |
| 128 | run | 364000 | 5.495369e-04 | 2.439 |
| 256 | ...ator\05_dataset\data_conv256\se_n8p0_Re1000_N256_ckpt.npz | 225000 | 1.000460e-03 | 1.778 |
| 512 | ...rator\05_dataset\data_convHR\se_n8p0_Re1000_N512_ckpt.npz | 475000 | 1.927010e-03 | 1.465 |

The series increases with N and `P/Phi` is not unity, so it must not be presented as
a grid-converged or verified global power balance.

## Outputs

* `plid_npz_inventory.csv`, `plid_dataset_summary.csv`, `plid_source_facts.csv`,
`plid_existing_estimates.csv`, `plid_audit_report.md`.
