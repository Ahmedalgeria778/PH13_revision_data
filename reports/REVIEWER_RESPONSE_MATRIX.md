# Final reviewer-response matrix (2026-11-25)

The editor decision and the original referee reports are retained in
`ORIGINAL_REFEREE_REPORTS_2026-11-25.txt`. The formal response is
`RESPONSE_LETTER_FINAL.tex` / `RESPONSE_LETTER_FINAL.pdf` (14 pages). Every
original comment in that letter is quoted without paraphrase. Each quotation is
followed by a **Revision made.** statement; where no change was appropriate, the
letter gives an explicit justification. No recalled or reconstructed comments
are used.

The decision record lists Referees #1, #2, #4, #5 and #6. DeepONet /
operator-learning material was removed from the final main article and
supplement, explicitly in response to Referee #1 major comment 4 and reiterated
in the responses to Referees #2, #4, #5 and #6.

## 1. Per-referee response structure

| Referee | Original comments answered | Main concerns addressed |
|---|---:|---|
| 1 | 7 | Excessive length and hard-to-follow writing; abstract narrative; shallow `D/A` trough on a resolution-biased baseline; removal of the DeepONet section; minor presentation point; recommendation |
| 2 | 7 | Description of continuous geometric deformation; summary paragraphs and major remarks on the physical mechanism, square-limit lid law, junction/energy conventions, normalization and the attached review report |
| 4 | 21 | Summary, review opening, five numbered concerns, overall assessment and the full attached report (abstract, introduction, Sections 3.3, 4–5, 6 and 7–8) |
| 5 | 9 | Short summary, abstract, introduction/background bullets, Section 3.3, Sections 4–5, Section 6, and Sections 7–8 |
| 6 | 10 | Short summary, abstract, three introduction bullets, Section 3.3, two Sections 4–5 bullets, Section 6 and Sections 7–8 |

Total: **54 verbatim original comments**, each followed by a revision action or
an explicit justification.

## 2. Revision actions by topic

| Topic | Final action | Location |
|---|---|---|
| Title and scope | Lowered the mid-title to ``continuously deformable''; recentred the paper on fluid physics. | Main title and abstract; response preamble |
| Abstract | Replaced by the 230-word version with symbols counted and abbreviations/symbols defined at first occurrence; the response letter now states ``about 230 words''. | Main abstract; response preamble |
| DeepONet / operator learning | Removed from the clean main article and supplement; no ML-based physical claim remains. | Response to Referee #1 major comment 4 and the corresponding comments of Referees #2, #4, #5 and #6 |
| Resolution and shallow minima | Sampled crossings and fitted minima are diagnostics; no grid-independent dissipation or universal optimum is claimed. The `D/A(3)/D/A(4)` crossing slopes are about `−95`, `−108` and `−101` in `Re` per unit `ln N`. | Main Abstract, Secs. 5–6; Supplement S12–S14 |
| Common-support LBM/FEM | Corrected common-support comparison gives `ε_D = 0.06–6.52%`; representative `n=4, Re=1000` values are `D_LBM = 0.0255896185899`, `D_FEM = 0.0246197180024`, `ε_D = 3.9395%`. The full-domain/FEM-mask ratio `1.63–2.06` identifies a support effect; a fixed-support FEM/LBM test at `r0>0` and `N=128/256` was not run. | Main Sec. 6; Supplement S7; `data/final_revision/common_support_dissipation.csv` |
| Junction cutoffs and log fits | Junction shares are `7.3–15.5%` (`N=128`) and `11.3–20.1%` (`N=256`) at `r=0.05L_c`; fixed junction-disk radii reduce the median `D_256/D_128−1` from `21.37%` to `8.77%` but leave residual drift. In Table S28 the `r0=0.5` ladder has observed orders `0.71` and `0.79` with a Richardson limit near `0.0244`; the unexcised series remains descriptive of logarithmic growth. Logarithmic fits remain descriptive only. | Main Sec. 5; Supplement S8, Tables S28–S29 |
| Diffusive-scaling check | At `n=4, Re=1000`, `N=128/256/384/512`, `U_lid=0.05*128/N` and `tau ≈ 0.519`, the `r0=0.5` values agree with production to within `5.3e-06` on `N=128`--`512` and the observed order stays about `1.01`; lowering the lattice Mach number does not remove the junction-excised drift. No Mach/acoustic explanation is established. | Main Sec. 5; Supplement S17, Table S30 |
| Wall/core budget | Maximum additivity residual `2.78e-17` over 506 rows; the `87.8%` value is the core share of the `n=4→8` rise, not of absolute dissipation. | Main Sec. 5; Supplement S6 |
| Square-limit lid law | The `n→∞` geometry is a square with piecewise tangential wall motion, not the classical Ghia boundary condition. | Main Secs. 2 and 6; Supplement S15 |
| Projected-lid control | Completed 13 matched fields; raw `D/A_mask` ratios `0.391–0.906`, boundary-velocity integral ratio `0.5`, forcing-normalized ratios `0.782–1.813`, and `KE/A` ratios `0.768–2.291`. The sampled argmin moves `n=4→2` but is only bracketed between `n=1.5` and `n=4`. Reported as a coupled geometry/forcing control, not causal isolation. | Main ``Scope and limitations''; Supplement S15, Table S23 and Fig. S13 |
| Junction and energy conventions | No regularization length; strict `y>0` assignment; archived flux ratio `-4.419`; no verified lid power or global energy closure. | Main Secs. 5–6; Supplement S8–S10 |
| Fixed-wall-support diagnostic | On production $n=4$, $Re=1000$ fields $N=128$--$512$, `D_core(delta=0.05 L_c)` and `D_core(delta=0.10 L_c)` change by `2.8%` and `6.7%`, against `16.9%` for `D_r0=0.5`; the remaining drift is associated with the retained near-wall support, not with core gradients on a fixed physical support, and is not a continuum certification. | Supplement S17, Table S31 |
| Accessibility and submission files | Separate Microsoft Word alt-text document supplied; alt text is not printed in the PDFs; clean and true marked-up versions supplied; figures embedded at their exact in-text locations. | `Alt_Text.docx`, `Article_File.pdf`, `Marked-Up_Manuscript.pdf`, `Supplementary_Article_File.pdf`, `Marked-Up_Supplementary.pdf` |
| Figures and table placement | The saturating heatmap was replaced by normalized $D/A$ curves; Figure 3 is now one full-width kinetic-energy panel, with verification panels retained in the supplement and captioned with their actual case settings. Detailed kinetic, fit-window, crossing and FEM tables are in the supplement. | Main Figs. 2–3; Supplement Figs. S4 and S14 and Tables S24–S30 |

## 3. Final document state

* Clean main article: `Article_File.tex` / `.pdf`, **19 pages**, seven physics-only sections, no undefined references or overfull warnings.
* Clean supplement: `Supplementary_Article_File.tex` / `.pdf`, **29 pages**, one coherent S1–S17 document, no undefined references or overfull warnings.
* Marked-up main article: `Marked-Up_Manuscript.tex` / `.pdf`, **21 pages**, true word/sentence-level differential (blue additions, red deletions, black unchanged text).
* Marked-up supplement: `Marked-Up_Supplementary.tex` / `.pdf`, **31 pages**, generated from the same clean-source lineage.
* Response letter: `RESPONSE_LETTER_FINAL.tex` / `.pdf`, **14 pages**, 54 verbatim comments.
* Repository: <https://github.com/Ahmedalgeria778/PH13_revision_data>, with English MIT `LICENSE`.

## 4. Withdrawn formulations

* ``the drift is not a resolution artefact'' → fitted locations are similar on matched grids, but absolute levels remain resolution-sensitive.
* ``the wall layer sets its location'' → the shallow minimum is a wall/core compensation.
* ``total momentum content'' → integrated kinetic energy.
* ``resolution-independent to about 2%'' → resolution-sensitive shallow optimum.
* ``onset'' / ``topologically distinct'' → `1%` detection-threshold crossing bracket.
* ``classical square cavity recovered asymptotically'' → square limit with piecewise tangential wall motion.
* ``no converged projected-lid fields'' → completed 13-field projected-lid control (coupled diagnostic; sampled minimum only bracketed between `n=1.5` and `n=4`).

## 5. Retained limitations

* No grid-independent continuum dissipation is claimed.
* No global energy-balance closure from archived macroscopic fields.
* No absolute dissipation value at `N=128` presented as converged.
* No universal or resolution-independent minimum.
* No verified `P_lid`.
* No topological inference from a sub-percent crossing.
* No causal isolation of curvature, confinement or wall kinematics from the projected-lid control.
* No separate Reviewer #3 response; no report was supplied.
