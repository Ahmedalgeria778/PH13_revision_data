# Point-by-Point Response to the Reviewers

**Journal:** Physics of Fluids  
**Manuscript:** *Geometry-induced reorganization of viscous dissipation in superelliptic lid-driven cavities*  
**Author:** BENIAICHE Ahmed

> We thank the Associate Editor and the Reviewers for their careful reading and for the constructive comments, which have led us to substantially revise the manuscript. The main article has been restructured as a physics-only seven-section manuscript, and the supplementary material has been rebuilt as a single coherent document containing only publication-ready supporting fluid-physics material. All numerical results quoted below were regenerated from the archived fields or from targeted Taylor–Hood P2/P1 finite-element solves; no new lattice Boltzmann campaign was launched. A clean version of the revised article, the final single-part supplement and the public data repository are provided together with this response letter. Below, each recalled comment is followed by a statement of the revision made, or by an explicit justification where no change was appropriate. The original full referee reports were not supplied to us for Reviewers 1, 2, 4, 5 and 6, and no separate report was supplied for Reviewer 3; the comments recalled below are therefore faithful abbreviated reconstructions from the audit matrix, the numbered validation reports and the reviewer identifiers retained in the revision record, and they are not verbatim quotations. Their wording can be replaced by the exact referee text if the reports are provided, without changing the scientific responses. No point-by-point reply is fabricated for Reviewer 3.

---

## Referee \#1

<span style="color:#003366">**Question R1-1.** Wall-curvature diagnostic: unit-circle test, arclength interpolation and recomputation of the database.</span>

**Revision made.** We agree that the diagnostic had to be rebuilt. The production algorithm interpolated only a short initial segment of the dense periodic arclength table, which collapsed the boundary samples onto two short arcs. For the unit circle, whose exact curvature is unity, the defective diagnostic returned $\kappa_{w,\max}=29.87$ and $\kappa_{w,\mathrm{rms}}=4.01$ with $f_{\mathrm{sharp}}=0.087$. The final algorithm interpolates the full periodic table, uses periodic central differences for the tangent angle and a wrapped angular difference for the window curvature. It now returns $\kappa_{w,\max}=\kappa_{w,\mathrm{rms}}=1.000000$ and $f_{\mathrm{sharp}}=0$ at every resolution and window tested.

- **Action.** All 190 curvature rows were recomputed with the final window $w=0.05L_c$ and the sharp-set threshold $\kappa_w\ge2\langle|\kappa|\rangle_\Gamma$.
- **Evidence.** `scripts/curvature/curvature_fixed.py`, `data/curvature/curvature_corrected_190.csv`, `reports/curvature_validation_report.md`; final panels `fig_curvature.png` and `fig_nearwall_large_axes.png`.
- **Location.** Main Section 5.3; Supplement S5.

<span style="color:#003366">**Question R1-2.** Interpretation of curvature: the earlier claim that wall curvature alone locates the area-normalized dissipation minimum.</span>

**Revision made.** We withdrew the wall-only explanation. At fixed Reynolds number the Pearson correlation between $\kappa_{w,\mathrm{rms}}$ and $D/A_{\mathrm{mask}}$ is positive but decreases from $+0.834$ at $Re=100$ to $+0.709$ at $Re=1000$; the corresponding Spearman coefficient at $Re=1000$ is only $+0.115$, and the sharp-set fraction is negatively correlated at $Re=500$ and $Re=1000$ ($-0.068$ and $-0.238$). The corrected statistics therefore do not support a curvature-set optimum.

- **Action.** The low-loss band is now described as a compensation between decreasing wall loss and increasing core loss, using the additive wall/core budget rather than a wall-only mechanism.
- **Location.** Main Sections 3 and 5.3; Supplement S5–S6.

<span style="color:#003366">**Question R1-3.** Corner-secondary-eddy counts and the language used for threshold crossings.</span>

**Revision made.** No topological transition is claimed. The corner analysis now uses a $0.20L_c$ reporting band, a $0.25L_c$ search region and $s_{\mathrm{corner}}$ expressed in units of $L=L_c/2$; no extrapolated rows are retained. Counts that change between neighbouring sampled Reynolds numbers are reported as $1\%$ detection-threshold crossing brackets on the sampled grids.

- **Action.** We removed the terms "onset" and "topologically distinct", and no causal link is inferred between the weak corner extremum and the dissipation increase.
- **Evidence.** `data/final_supplement/corner_conv.csv`, `data/final_supplement/corner_bnd.csv`.
- **Location.** Supplement S13–S14.

---

## Referee \#2

<span style="color:#003366">**Question R2-1.** Junction treatment and dissipation budget (point \#2.4): is there a physical regularization length at the moving-wall junctions?</span>

**Revision made.** There is no physical regularization in the code. The tangential lid is assigned by the strict nodal test $y>0$: the left junction at $y=+1.22\times10^{-16}$ is moving and the right junction at $y=0$ is fixed. Dissipation inside disks of radius $r$ around these points is therefore a cutoff-dependent diagnostic, not a converged physical total and not a regularization length.

- **Action.** We report the junction share explicitly ($7.3$–$15.5\%$ at $r=0.05L_c$ and $22.6$–$42.6\%$ at $r=0.15L_c$ on $N=128$) and removed the claim that a power estimator had been verified.
- **Evidence.** `scripts/junction/junction_budget.py`, `data/junction/junction_budget.csv`, `data/junction/identity_check.csv`, `reports/junction_budget_report.md`; schematic `figures/final_supplement/fig_supp_fem_junction_schematic.png`.
- **Location.** Main Section 5.2; Supplement S8.

<span style="color:#003366">**Question R2-2.** Energy balance and lid power: can a global power–dissipation closure be inferred from the archived fields?</span>

**Revision made.** No. We keep three statements distinct: (i) the continuous mechanical-energy identity, (ii) the exact discrete lattice-Boltzmann balance, which would require same-step distribution functions, and (iii) the diagnostic computed from the archived macroscopic fields. The archived-field flux ratio is $-4.419$ instead of the expected $+1$, so it cannot be interpreted as an energy-balance closure.

- **Action.** No $P_{\mathrm{lid}}$ value is quoted in the main article or the supplement. The final 810 `.npz` fields contain no distribution functions $f$, whereas 148 checkpoint files contain $f$ and $it$; existing estimates give $P/\Phi=4.268$, $2.439$, $1.778$ and $1.465$ at $N=64$, $128$, $256$ and $512$, which is not grid-converged.
- **Evidence.** `scripts/final_revision/audit_plid.py`, `reports/plid_audit_report.md`, `data/final_revision/plid_npz_inventory.csv`.
- **Location.** Main Sections 5.2 and 6.3; Supplement S9–S10.

---

## Referee \#3

<span style="color:#003366">**Question R3.** No separate reviewer-3 report was supplied.</span>

**Justification for no change.** No point-by-point reply can be prepared for Reviewer 3 without the report, and no response is fabricated here. The FEM-gradient item tagged `\#3.3` in the internal audit trail was addressed together with Reviewer 4, Question R4-3, and the complete numerical record is available in the public repository.

---

## Referee \#4

<span style="color:#003366">**Question R4-1.** Square-limit boundary condition (point \#4.B1): does $n\to\infty$ recover the classical Ghia square cavity?</span>

**Revision made.** No. The domain tends geometrically to $[-1,1]^2$, but the tangential wall law does not tend to the Ghia condition. Because the moving part is defined by the strict test $y>0$, the upper halves of the vertical side walls remain in motion in the limiting geometry, downward on the right and upward on the left, while the lower halves remain fixed. The limit is therefore a square with piecewise tangential wall motion, not a square cavity with a uniformly translating upper wall.

- **Action.** The Ghia cavity is now presented as an independent solver-verification case with a different boundary law. The Introduction now defines the shape family explicitly: $n=2$ corresponds to a circular cavity, values below 2 produce diamond-like shapes with pointed ends, while increasing $n$ above 2 progressively flattens the sides and approaches a square-like geometry. A horizontally projected tangential law is defined only as a kinematic boundary-law convention; no converged fields were generated with it and no hydrodynamic sensitivity is inferred.
- **Evidence.** `reports/AUDIT_NOTES.md`, Section 2; `reports/junction_budget_report.md`, Section 1.
- **Location.** Main Sections 1–2 and 7; Supplement S15.

<span style="color:#003366">**Question R4-2.** Junction regularization (point \#4.4): should the junction contribution be treated as a converged physical quantity?</span>

**Revision made.** No. The junction assignment is a machine-precision-sensitive implementation detail of the strict $y>0$ switch, not a physical regularization length. We report the contribution as a function of the excision radius and state explicitly that it is cutoff-dependent; the archived-field identity diagnostic remains non-closed, as stated in the response to Reviewer 2.

- **Action.** No blending or smoothing length was introduced. The junction schematic, the cutoff diagnostic and the archived-field identity check are included in the supplement.
- **Evidence.** `data/junction/junction_budget.csv`, `data/junction/identity_check.csv`.
- **Location.** Main Section 5.2; Supplement S8.

<span style="color:#003366">**Question R4-3.** Finite-element gradients and integrated dissipation (point \#4.3): are the LBM/FEM differences validation errors or different reconstructions?</span>

**Revision made.** We assembled $D_{\mathrm{FEM}}^{\Omega}=2\nu\int_\Omega S(\mathbf{u}_h):S(\mathbf{u}_h)\,dA$ directly from the P2 strain field on a mesh ladder. Mesh levels 4/5/6 contain 1,024/4,096/16,384 triangles and 4,771/18,755/74,371 velocity-plus-pressure unknowns; all 36 Picard solves converged at $10^{-9}$ in 14–34 iterations. On a common support the relative dissipation discrepancy is $\varepsilon_D=0.72$–$20.02\%$ over 9,488–15,168 masked nodes, with $D_{\mathrm{FEM}}^{\Omega}/D_{\mathrm{FEM}}^{M}=1.63$–$2.06$.

- **Action.** The column formerly labelled "rel. $D$ error" is identified as $|D_{\mathrm{FD,lattice}}-D_{\mathrm{exact,lattice}}|/D_{\mathrm{exact,lattice}}$, a finite-difference reconstruction diagnostic on sampled FEM fields, not an LBM/FEM validation error. Richardson and incremental extrapolations are reported only as sensitivity diagnostics, not as asymptotic bounds.
- **Evidence.** `scripts/fem/fem_dissipation_validation.py`, `scripts/fem/fem_gradient_reconstruction.py`, `reports/fem_validation_report.md`; `data/final_revision/common_support_dissipation.csv`.
- **Location.** Main Section 6.2; Supplement S7–S8.

<span style="color:#003366">**Question R4-4.** Normalization and the factor of two in the dissipation definition.</span>

**Revision made.** The same mechanical definition is used on both sides: $D=2\nu\int S:S\,dA$ with $\nu=2/Re$ in paper units. The archived LBM velocities are lid-normalized with $U_{\mathrm{lid}}=0.05$, while the FEM solves use $U_{\mathrm{lid}}=1$ and the same paper-unit viscosity. The factor two is counted once.

- **Action.** We documented the pressure convention $p_{\mathrm{LBM}}=c_s^2(\rho_{\mathrm{LBM}}-1)$, $c_s^2=1/3$, and $p=(\rho-1)/(3U_{\mathrm{lid}}^2)$ in paper units.
- **Location.** Main Section 2; Supplement S7 and S9.

<span style="color:#003366">**Question R4-5.** Campaign inventory, matched grids and resolution claims.</span>

**Revision made.** The verified inventory is as follows. `data_all190` contains 190 fields; `data_refine` contains 50 fields at eight Reynolds numbers, $Re=\{300,325,350,500,850,875,900,1000\}$; the $N=256$ collection contains 63 fields, of which 62 are matched to the $N=128$ grid. The only unmatched pair is $(n,Re)=(4.25,300)$.

- **Action.** Fitted minimum locations are compared only on matched grids. Absolute $D$ at $N=128$ is not presented as grid-converged, and no universal or resolution-independent optimum is claimed.
- **Evidence.** `data/final_revision/campaign_inventory.csv`, `data/final_revision/campaign_N256_matching.csv`, `reports/campaign_verification.md`.
- **Location.** Main Table I and Section 6; Supplement S11.

---

## Referee \#5

<span style="color:#003366">**Question R5-1.** Additive wall/core dissipation budget (point \#5.3): does the wall layer set the minimum?</span>

**Revision made.** No. On a common integration mask the partition is exact: $D_{\mathrm{mask}}/A_{\mathrm{mask}}=D_{\mathrm{wall}}/A_{\mathrm{mask}}+D_{\mathrm{core}}/A_{\mathrm{mask}}$, with the same $A_{\mathrm{mask}}$ denominator in all three terms. The maximum absolute additivity residual over 506 rows is $2.78\times10^{-17}$. For $Re=1000$, $N=256$ and $\delta=0.05L_c$, the core contributes $87.8\%$ of the rise from $n=4$ to $n=8$; this is the share of the increase, not the absolute core share. Across all available increments the core share of the increase ranges from $61.5\%$ to $99.8\%$.

- **Action.** The wall-only claim was removed from the Abstract, Introduction, Results and Conclusions, and the increment-based interpretation is stated wherever the $87.8\%$ value appears.
- **Evidence.** `scripts/core_wall/core_wall_budget.py`, `data/core_wall/core_wall_budget.csv`, `reports/core_wall_budget_report.md`; figure `figures/fig_core_wall_budget.png`.
- **Location.** Main Sections 3 and 5.1; Supplement S6.

<span style="color:#003366">**Question R5-2.** Qualification of the minima and of apparent transitions.</span>

**Revision made.** We report sampled grid extrema separately from ordinary-least-squares quadratic fits on three- and five-point supports. At $Re=1000$ the fitted $n^*_{D/A}$ changes from $4.065$ with a three-point support to $4.471$ with a five-point support, and $n^*_D$ changes from $2.794$ to $2.381$; fitted locations on matched grids are similar, but absolute $D$ levels remain resolution-sensitive. The supports, exclusions and estimator are documented in the supplement.

- **Action.** We no longer use "onset" or "topologically distinct". Reynolds crossings are reported as $1\%$ detection-threshold crossing brackets on the sampled grids, and no extrapolated minima or thresholds are quoted as converged values.
- **Evidence.** `scripts/minima/minima_qualification.py`, `data/minima/fit_diagnostics.csv`, `data/minima/crossing_diagnostics.csv`, `reports/minima_qualification_report.md`.
- **Location.** Main Sections 6.1–6.2; Supplement S12.

---

## Referee \#6

<span style="color:#003366">**Question R6-1.** Moving-lid arclength $L_{\mathrm{mov}}$ and its limiting values.</span>

**Revision made.** The upper-half moving-wall arclength for $L_c=2$ is $2.8789718432636$ at $n=1.25$, $\pi$ at $n=2$, $3.5088489717820$ at $n=4$ and $3.7389869262423$ at $n=8$. The diamond, circle and square-limit cases were checked independently.

- **Action.** We state explicitly that the geometric square limit has piecewise tangential motion and is not the Ghia square cavity; the projected lid is a boundary-law definition only.
- **Evidence.** `scripts/final_revision/compute_lmov.py`, `data/final_revision/l_mov.csv`, `data/final_revision/l_mov_validation.csv`.
- **Location.** Supplement S10.

<span style="color:#003366">**Question R6-2.** Reproducibility, data deposit and scope of the numerical evidence.</span>

**Revision made.** The public repository <https://github.com/Ahmedalgeria778/PH13_revision_data> contains the final single-part supplement in source and PDF form, the analysis scripts, regenerated figures, result tables, validation reports, a reproduction README and an English MIT `LICENSE` with the copyright notice. It deliberately does not contain the main-article source or PDF, and it does not contain the raw archived `.npz` fields because of their size.

- **Action.** The Data availability statement now gives the repository URL and mentions the README and the MIT license. We did not run a new LBM campaign: the deposited evidence consists of read-only post-processing of archived fields plus targeted Taylor–Hood P2/P1 solves used only for verification.
- **Evidence.** <https://github.com/Ahmedalgeria778/PH13_revision_data>; `LICENSE`, `README.md`, `supplement/PH13_supplementary_final.pdf`.
- **Location.** Main Data availability statement; repository README.

---

We thank the reviewers again for the thorough and constructive reports, which have substantially improved the clarity and the honesty of the manuscript. The remaining limitations are stated explicitly: no global energy closure, no verified $P_{\mathrm{lid}}$, no grid-converged absolute dissipation at $N=128$, and no universal or resolution-independent minimum.

Sincerely,

BENIAICHE Ahmed
