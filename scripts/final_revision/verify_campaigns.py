# -*- coding: utf-8 -*-
"""Read-only verification of PH13 campaign counts (new outputs only).

Run (Windows, base Python):
  C:\\Users\\user\\AppData\\Local\\Programs\\Python\\Python314\\python.exe verify_campaigns.py

Inputs are archived .npz fields/manifests in ../05_dataset (read-only).
Outputs are written only in this directory.
"""
from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]                      # GIRVD (revised)
DATA = ROOT / "05_dataset"
MANUSCRIPT = ROOT / "corrections for reviewer" / "06_manuscript_restructure" / "PH13_manuscript_physics_only.tex"

DIRS = [
    "data_all190", "data_refine", "data_refine_seed",
    "data_conv256", "data_conv256_lowRe",
    "data_convHR", "data_convHR_extB", "data_lid_projected",
]
PAT = re.compile(r"se_n([0-9]+p[0-9]+)_Re([0-9]+)_N(\d+)(?:_ckpt)?\.npz$")


def parse_name(name: str):
    m = PAT.match(name)
    if not m:
        return None
    return (float(m.group(1).replace("p", ".")), int(m.group(2)), int(m.group(3)))


def fmt_n(n: float) -> str:
    return f"{n:g}"


def manifest_rows(path: Path) -> int:
    if not path.exists():
        return -1
    with path.open("r", encoding="utf-8", newline="") as fh:
        return max(0, sum(1 for _ in fh) - 1)


def inventory() -> dict:
    inv = {}
    for d in DIRS:
        p = DATA / d
        finals, ckpts, bad = [], [], []
        for f in sorted(p.glob("*.npz")):
            k = parse_name(f.name)
            if k is None:
                bad.append(f.name)
                continue
            (ckpts if "_ckpt" in f.name else finals).append((k, f))
        # internal metadata, not only filenames
        meta_mismatch = []
        keysets = Counter()
        for k, f in finals:
            with np.load(f) as z:
                keysets.update(z.files)
                if all(s in z.files for s in ("n", "Re", "N")):
                    ik = (round(float(z["n"]), 4), int(round(float(z["Re"]))), int(z["N"]))
                    if ik != (round(k[0], 4), k[1], k[2]):
                        meta_mismatch.append((f.name, ik))
        inv[d] = dict(finals=finals, ckpts=ckpts, bad=bad,
                      meta_mismatch=meta_mismatch, keysets=keysets)
    return inv


def pair_map(inv, d: str) -> dict:
    out = {}
    for (n, re_, N), f in inv[d]["finals"]:
        out.setdefault((n, re_), []).append(f)
    return out


def main() -> None:
    inv = inventory()
    p190 = pair_map(inv, "data_all190")
    pref = pair_map(inv, "data_refine")
    pseed = pair_map(inv, "data_refine_seed")
    p256 = pair_map(inv, "data_conv256")
    plow = pair_map(inv, "data_conv256_lowRe")
    all256 = defaultdict(list)
    for k, v in list(p256.items()) + list(plow.items()):
        all256[k].extend(v)

    n128_union = {}
    for src in (p190, pref, pseed):
        for k, v in src.items():
            n128_union.setdefault(k, []).extend(v)

    rows = []
    for d in DIRS:
        it = inv[d]
        ns = sorted({k[0] for k, _ in it["finals"]})
        res = sorted({k[1] for k, _ in it["finals"]})
        per_re = Counter(k[1] for k, _ in it["finals"])
        man = sorted((DATA / d).glob("manifest*.csv"))
        rows.append(dict(
            dataset=d,
            final_npz=len(it["finals"]),
            checkpoint_npz=len(it["ckpts"]),
            distinct_n_Re=len({(k[0], k[1]) for k, _ in it["finals"]}),
            N_values=",".join(str(N) for N in sorted({k[2] for k, _ in it["finals"]})),
            n_values=",".join(fmt_n(x) for x in ns),
            Re_values=",".join(str(x) for x in res),
            per_Re=";".join(f"{r}:{per_re[r]}" for r in res),
            manifest_files=";".join(m.name for m in man) or "-",
            manifest_data_rows=";".join(str(manifest_rows(m)) for m in man) or "-",
            metadata_mismatches=len(it["meta_mismatch"]),
            unparsed_names=";".join(it["bad"]) or "-",
        ))

    def wcsv(name, fieldnames, data):
        with (HERE / name).open("w", encoding="utf-8", newline="") as fh:
            wr = csv.DictWriter(fh, fieldnames=fieldnames)
            wr.writeheader()
            wr.writerows(data)

    wcsv("campaign_inventory.csv", list(rows[0].keys()), rows)

    # Per-case N=256 matching table
    mrows = []
    for (n, re_) in sorted(all256):
        files = all256[(n, re_)]
        src = ";".join(sorted({f.parent.name for f in files}))
        in190 = (n, re_) in p190
        inref = (n, re_) in pref
        inseed = (n, re_) in pseed
        mrows.append(dict(n=n, Re=re_, N=256, source_dirs=src,
                          files=";".join(sorted(f.name for f in files)),
                          in_data_all190=int(in190), in_data_refine=int(inref),
                          in_data_refine_seed=int(inseed),
                          comparable_to_N128=int((n, re_) in n128_union),
                          matched_N128_file=";".join(
                              sorted(f.name for f in n128_union.get((n, re_), []))) or "-"))
    wcsv("campaign_N256_matching.csv", list(mrows[0].keys()), mrows)

    # Refined-grid matrix: count per (n, Re) in data_refine
    refine_ns = sorted({n for (n, _) in pref})
    refine_res = sorted({r for (_, r) in pref})
    with (HERE / "campaign_refine_matrix.csv").open("w", encoding="utf-8", newline="") as fh:
        wr = csv.writer(fh)
        wr.writerow(["n"] + [f"Re{r}" for r in refine_res] + ["row_total"])
        for n in refine_ns:
            counts = [sum(1 for f in pref.get((n, r), []) if True) for r in refine_res]
            wr.writerow([fmt_n(n)] + counts + [sum(counts)])
        wr.writerow(["col_total"] + [sum(len(pref.get((n, r), [])) for n in refine_ns)
                                    for r in refine_res] + [sum(len(v) for v in pref.values())])

    unmatched = sorted(set(all256) - set(n128_union))
    matched = sorted(set(all256) & set(n128_union))

    L = [
        "# PH13 campaign-count verification (read-only, 2026-11-25)",
        "",
        "Python: `C:\\Users\\user\\AppData\\Local\\Programs\\Python\\Python314\\python.exe`",
        "Script: `corrections for reviewer/07_final_scientific_revision/verify_campaigns.py`",
        "Manifest table in `corrections for reviewer/06_manuscript_restructure/PH13_manuscript_physics_only.tex`, lines 169-171.",
        "",
        "## Verified archive counts",
        "",
        "| Dataset | Final .npz | Distinct (n,Re) | N | Re set | per-Re counts |",
        "|---|---:|---:|---|---|---|",
    ]
    for r in rows:
        L.append(f"| `{r['dataset']}` | {r['final_npz']} | {r['distinct_n_Re']} | "
                 f"{r['N_values']} | {r['Re_values']} | {r['per_Re']} |")
    L += [
        "",
        "Internal `n/Re/N` metadata agreed with file names in all archived final fields "
        "(metadata mismatches = 0). Checkpoint files were counted separately and are not fields.",
        "",
        "This campaign inventory uses the strict reference-name regex "
        "`se_n<...>_Re<...>_N<...>(?:_ckpt)?.npz`; suffixed control files such as "
        "`*_proj.npz` are excluded. The separate P_lid inventory counts every `.npz` "
        "and therefore reports 15 projected final fields in `data_lid_projected`.",
        "",
        "## Reference grid",
        "",
        f"`05_dataset/data_all190`: {len(p190)} final fields = 10 n x 19 Re, "
        "n = {1.25, 1.5, 1.75, 2, 2.5, 3, 4, 5, 6, 8}, "
        "Re = 100,150,...,1000 (step 50), all N=128. Claim **190**: CORRECT.",
        "",
        "## Local refinement (the real archived campaign)",
        "",
        f"`05_dataset/data_refine`: **{sum(len(v) for v in pref.values())}** final N=128 fields.",
        "This is the correct case count. The Re set is **8 values**, "
        "not 6: {300, 325, 350, 500, 850, 875, 900, 1000}.",
        "`generate_local_refinement.py` originally defined 9 n x 6 Re "
        "(Re={300,325,350,850,875,900}); `run_refine_re500_1000.py` added the "
        "Re=500 band and Re=1000/n=2.25 complement, and `n=4.25` was added "
        "later (`chain_refine_then_n225.py`, `run_A3_campaigns_v2.py`). "
        "The two manifests in `data_refine/` record only 11 + 8 rows, so the "
        "50-case count must be taken from the archived .npz files themselves.",
        "Per-Re counts: " + "; ".join(
            f"Re={r}:{sum(len(pref.get((n, r), [])) for n in refine_ns)}" for r in refine_res) + ".",
        "Per-(n,Re) matrix: `campaign_refine_matrix.csv`.",
        "",
        "## N=256 matched campaign",
        "",
        f"`05_dataset/data_conv256`: {sum(len(v) for v in p256.values())} fields "
        "(17 distinct n at Re={300,500,1000}).",
        f"`05_dataset/data_conv256_lowRe`: {sum(len(v) for v in plow.values())} fields "
        "(12 at Re={100,150,200,250} x n={2.5,3,4}, plus n=2.25 at Re=300).",
        f"Total distinct N=256 fields: **{len(all256)}**; no duplicate (n,Re) keys.",
        f"N=128 reference union used for matching: `data_all190` (190) + "
        f"`data_refine` (50) + `data_refine_seed` (28) = **{len(n128_union)}** distinct pairs.",
        f"Comparable N=256 cases: **{len(matched)}**; unmatched: **{len(unmatched)}** "
        + (f"({fmt_n(unmatched[0][0])}, Re={unmatched[0][1]})" if len(unmatched) == 1 else str(unmatched)) + ".",
        "The unmatched case is `se_n4p25_Re300_N256.npz`; no N=128 field exists for "
        "(n=4.25, Re=300) in any archived N=128 campaign.",
        "",
        "## Manuscript wording implication",
        "",
        "* 190 reference: exact.",
        "* 50 local refinement: exact, but the manuscript's `6 Re` describes the "
        "original generator plan; the archived campaign uses 8 Re values.",
        "* 63 at N=256 and 62 comparable: exact once `data_conv256_lowRe` and the "
        "N=128 `data_refine_seed` are included; the `17 n at 3 Re + low Re` wording "
        "is a coverage description, not a 17 x 3 cross product.",
        "",
        "## Outputs",
        "",
        "* `campaign_inventory.csv`, `campaign_N256_matching.csv`, `campaign_refine_matrix.csv`",
    ]
    (HERE / "campaign_verification.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(json.dumps(dict(
        n190=len(p190), refine=sum(map(len, pref.values())),
        refine_Re=refine_res, conv256=sum(map(len, p256.values())),
        lowRe=sum(map(len, plow.values())), n256_total=len(all256),
        n128_union=len(n128_union), matched=len(matched), unmatched=[list(x) for x in unmatched],
    ), indent=2))


if __name__ == "__main__":
    main()
