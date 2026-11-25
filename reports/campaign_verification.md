# PH13 campaign-count verification (read-only, 2026-11-25)

Python: `C:\Users\user\AppData\Local\Programs\Python\Python314\python.exe`
Script: `corrections for reviewer/07_final_scientific_revision/verify_campaigns.py`
Manifest table in `corrections for reviewer/06_manuscript_restructure/PH13_manuscript_physics_only.tex`, lines 169-171.

## Verified archive counts

| Dataset | Final .npz | Distinct (n,Re) | N | Re set | per-Re counts |
|---|---:|---:|---|---|---|
| `data_all190` | 190 | 190 | 128 | 100,150,200,250,300,350,400,450,500,550,600,650,700,750,800,850,900,950,1000 | 100:10;150:10;200:10;250:10;300:10;350:10;400:10;450:10;500:10;550:10;600:10;650:10;700:10;750:10;800:10;850:10;900:10;950:10;1000:10 |
| `data_refine` | 50 | 50 | 128 | 300,325,350,500,850,875,900,1000 | 300:6;325:9;350:6;500:7;850:6;875:9;900:6;1000:1 |
| `data_refine_seed` | 28 | 28 | 128 | 100,200,1000 | 100:10;200:9;1000:9 |
| `data_conv256` | 50 | 50 | 256 | 300,500,1000 | 300:16;500:17;1000:17 |
| `data_conv256_lowRe` | 13 | 13 | 256 | 100,150,200,250,300 | 100:3;150:3;200:3;250:3;300:1 |
| `data_convHR` | 12 | 6 | 384,512 | 300,1000 | 300:4;1000:8 |
| `data_convHR_extB` | 24 | 12 | 384,512 | 100,150,200,250 | 100:6;150:6;200:6;250:6 |
| `data_lid_projected` | 0 | 0 |  |  |  |

Internal `n/Re/N` metadata agreed with file names in all archived final fields (metadata mismatches = 0). Checkpoint files were counted separately and are not fields.

This campaign inventory uses the strict reference-name regex `se_n<...>_Re<...>_N<...>(?:_ckpt)?.npz`; suffixed control files such as `*_proj.npz` are excluded. The separate P_lid inventory counts every `.npz` and therefore reports 15 projected final fields in `data_lid_projected`.

## Reference grid

`05_dataset/data_all190`: 190 final fields = 10 n x 19 Re, n = {1.25, 1.5, 1.75, 2, 2.5, 3, 4, 5, 6, 8}, Re = 100,150,...,1000 (step 50), all N=128. Claim **190**: CORRECT.

## Local refinement (the real archived campaign)

`05_dataset/data_refine`: **50** final N=128 fields.
This is the correct case count. The Re set is **8 values**, not 6: {300, 325, 350, 500, 850, 875, 900, 1000}.
`generate_local_refinement.py` originally defined 9 n x 6 Re (Re={300,325,350,850,875,900}); `run_refine_re500_1000.py` added the Re=500 band and Re=1000/n=2.25 complement, and `n=4.25` was added later (`chain_refine_then_n225.py`, `run_A3_campaigns_v2.py`). The two manifests in `data_refine/` record only 11 + 8 rows, so the 50-case count must be taken from the archived .npz files themselves.
Per-Re counts: Re=300:6; Re=325:9; Re=350:6; Re=500:7; Re=850:6; Re=875:9; Re=900:6; Re=1000:1.
Per-(n,Re) matrix: `campaign_refine_matrix.csv`.

## N=256 matched campaign

`05_dataset/data_conv256`: 50 fields (17 distinct n at Re={300,500,1000}).
`05_dataset/data_conv256_lowRe`: 13 fields (12 at Re={100,150,200,250} x n={2.5,3,4}, plus n=2.25 at Re=300).
Total distinct N=256 fields: **63**; no duplicate (n,Re) keys.
N=128 reference union used for matching: `data_all190` (190) + `data_refine` (50) + `data_refine_seed` (28) = **259** distinct pairs.
Comparable N=256 cases: **62**; unmatched: **1** (4.25, Re=300).
The unmatched case is `se_n4p25_Re300_N256.npz`; no N=128 field exists for (n=4.25, Re=300) in any archived N=128 campaign.

## Manuscript wording implication

* 190 reference: exact.
* 50 local refinement: exact, but the manuscript's `6 Re` describes the original generator plan; the archived campaign uses 8 Re values.
* 63 at N=256 and 62 comparable: exact once `data_conv256_lowRe` and the N=128 `data_refine_seed` are included; the `17 n at 3 Re + low Re` wording is a coverage description, not a 17 x 3 cross product.

## Outputs

* `campaign_inventory.csv`, `campaign_N256_matching.csv`, `campaign_refine_matrix.csv`
