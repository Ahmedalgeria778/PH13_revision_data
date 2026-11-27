================================================================================
PH13 -- PHYSICS OF FLUIDS SUBMISSION PACKAGE (file guide)
================================================================================

Manuscript title: Geometry-induced reorganization of viscous dissipation in
continuously deformable superelliptic lid-driven cavities
Journal: Physics of Fluids
Author: BENIAICHE Ahmed

--------------------------------------------------------------------------------
FILES TO SELECT WHEN UPLOADING
--------------------------------------------------------------------------------
1. Manuscript File (TeX) ............... Article_File.tex
2. Manuscript PDF ....................... Article_File.pdf
   Use the "Manuscript PDF" Browse button next to the TeX file. All figures
   and tables are embedded in this PDF at their exact in-text locations;
   no figures are uploaded as separate files.
3. Marked-Up Manuscript ................. Marked-Up_Manuscript.tex
                                          Marked-Up_Manuscript.pdf
   True word/sentence-level differential against the preceding clean source.
   Additions are blue and deletions are red. The markup is not a blanket
   colouring of whole sections.
4. Supplementary Online Material ........ Supplementary_Article_File.tex
                                          Supplementary_Article_File.pdf
   Upload with file type "Supplementary Online Material". All floats are at
   their exact in-text source locations.
5. Marked-Up Supplementary .............. Marked-Up_Supplementary.tex
                                          Marked-Up_Supplementary.pdf
   Differential markup against the preceding clean supplementary source,
   using the same blue-addition/red-deletion convention.
6. Alt Text (Microsoft Word) ............ Alt_Text.docx
   Upload this Word file for the AIP accessibility requirement. A plain-text
   mirror, Alt_Text.txt, is included for convenience but is not a substitute
   for the Word document. The clean article and supplementary PDFs also carry an Alt text line immediately after every figure and table.
7. Response Letter ...................... RESPONSE_LETTER_FINAL.pdf
   Also supplied as RESPONSE_LETTER_FINAL.tex for editing. Every original
   referee comment is quoted from the referee reports, followed by the
   revision made or an explicit justification for no change.
8. Highlight Image ...................... Highlight_Image.tif
   (Highlight_Image.jpeg is an equivalent alternative.)
   Exact size 8.0139 in x 6.2739 in = 2404 x 1882 px at 300 dpi.

--------------------------------------------------------------------------------
ADDITIONAL TEX FILES
--------------------------------------------------------------------------------
The bibliography is embedded in the article and supplement with the
thebibliography environment; no separate .bib file is needed. No custom .sty
or .cls file is used. The following table fragments are included by \input
and must remain beside the TeX files for local recompilation:

  Main article:     none; all tables are embedded in Article_File.tex
  Supplement:       supp_corewall_target_table.tex,
                    supp_corewall_changes_table.tex,
                    supp_common_support_table.tex, supp_lmov_table.tex,
                    junction_cutoff_table.tex, junction_logfit_table.tex,
                     projected_lid_table.tex, kinetic_table.tex,
                     fem_table.tex

The folders figs_new/ and figs/ contain the source images used by the TeX
files. They are provided only so the PDFs can be rebuilt locally; the journal
extracts the published figures directly from the uploaded PDFs, so these image
folders are not manuscript files to select during upload.

--------------------------------------------------------------------------------
SCIENTIFIC CONTROLS INCLUDED
--------------------------------------------------------------------------------
The revision includes corrected common-support LBM/FEM dissipation, fixed
junction-disk radii with observed orders and a Richardson diagnostic in Table S28,
a production-family diffusive-scaling check in Table S30,
descriptive logarithmic junction fits, resolution checks
through N=512, and the targeted projected-lid campaign at n=1.5, 2, 4 and 8,
Re=100 and 1000 on N=128 with selected N=256 comparisons. Across the 13
matched fields, raw projected/tangential D/A_mask ratios are 0.391--0.906;
the imposed boundary-velocity integral ratio is 0.5, so forcing-normalized
ratios are 0.782--1.813. Normalization by KE/A instead gives 0.768--2.291.
The sampled argmin moves from n=4 to n=2, but the projected continuous minimum
is only bracketed between n=1.5 and n=4. The projected-lid fields change both
forcing direction and geometry; they are reported as a
coupled control, not as causal isolation of curvature, confinement or wall
kinematics.

--------------------------------------------------------------------------------
ACCESSIBILITY
--------------------------------------------------------------------------------
Alt_Text.docx is the separate Microsoft Word alt-text document required by
AIP. It lists alt text for every figure and table in the clean Article File
and in the Supplementary Online Material. The same alt text is also printed
immediately after each float in Article_File.pdf and in the clean
supplementary PDF.

--------------------------------------------------------------------------------
REFEREE REPORTS
--------------------------------------------------------------------------------
The editor decision and the original reports for Referees #1, #2, #4, #5 and
#6 are followed in the response letter. The decision record lists these five
referees only; no Referee #3 passage is included.
================================================================================
