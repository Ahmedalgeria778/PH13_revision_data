# -*- coding: utf-8 -*-
"""Verify the requested core/wall budget numbers and generalize them.

Input (read-only):
  corrections for reviewer/04_additive_core_wall_budget/core_wall_budget.csv
Output (new files only): this directory.

Run:
  C:\\Users\\user\\AppData\\Local\\Programs\\Python\\Python314\\python.exe analyze_core_wall.py
"""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
CSV_IN = HERE.parent / "04_additive_core_wall_budget" / "core_wall_budget.csv"
NUM = ("n", "Re", "N", "delta_over_Lc", "A_mask", "D_mask", "D_wall", "D_core",
       "Dmask_over_A", "Dwall_over_A", "Dcore_over_A", "A_wall", "A_core",
       "f_wall", "f_core", "additivity_residual")


def load():
    rows = []
    with CSV_IN.open("r", encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            for k in NUM:
                r[k] = float(r[k])
            r["case_id"] = str(r["case_id"])
            rows.append(r)
    return rows


def write_csv(name, rows):
    if not rows:
        return
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with (HERE / name).open("w", encoding="utf-8", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=fields)
        wr.writeheader()
        wr.writerows(rows)


def delta_row(low, high, label):
    dt = high["Dmask_over_A"] - low["Dmask_over_A"]
    dw = high["Dwall_over_A"] - low["Dwall_over_A"]
    dc = high["Dcore_over_A"] - low["Dcore_over_A"]
    frac_c = dc / dt if dt != 0 else float("nan")
    frac_w = dw / dt if dt != 0 else float("nan")
    return dict(
        Re=int(low["Re"]), N=int(low["N"]), delta_over_Lc=low["delta_over_Lc"],
        comparison=label,
        n_low=low["n"], n_high=high["n"],
        DA_low=low["Dmask_over_A"], DA_high=high["Dmask_over_A"],
        wall_low=low["Dwall_over_A"], wall_high=high["Dwall_over_A"],
        core_low=low["Dcore_over_A"], core_high=high["Dcore_over_A"],
        delta_DA=dt, delta_wall=dw, delta_core=dc,
        core_fraction_of_rise=frac_c, wall_fraction_of_rise=frac_w,
        core_dominates=(bool(frac_c > 0.5) if dt > 0 else None),
        valid_rise=(bool(dt > 0)),
        f_core_low=low["f_core"], f_core_high=high["f_core"],
        n_grid=",".join(f"{x:g}" for x in sorted({r['n'] for r in LOW_HIGH_CACHE})),
    )


LOW_HIGH_CACHE = []


def main():
    rows = load()
    keys = [(round(r["n"], 4), int(r["Re"]), int(r["N"]), round(r["delta_over_Lc"], 4))
            for r in rows]
    assert len(rows) == 506, len(rows)
    assert len(set(keys)) == 506
    assert max(abs(r["additivity_residual"]) for r in rows) < 1e-15
    cases = {(round(r["n"], 4), int(r["Re"]), int(r["N"])) for r in rows}
    assert len(cases) == 253, len(cases)

    # -------- exact user target --------
    target = sorted((r for r in rows if int(r["N"]) == 256 and int(r["Re"]) == 1000
                     and abs(r["delta_over_Lc"] - 0.05) < 1e-12
                     and r["n"] in (2.0, 3.0, 4.0, 6.0, 8.0)), key=lambda r: r["n"])
    assert len(target) == 5, len(target)
    tgt_rows = []
    for r in target:
        tgt_rows.append(dict(n=r["n"], DA=r["Dmask_over_A"], wall=r["Dwall_over_A"],
                             core=r["Dcore_over_A"], f_wall=r["f_wall"], f_core=r["f_core"],
                             additivity_residual=r["additivity_residual"]))
    write_csv("core_target_Re1000_N256_d005.csv", tgt_rows)
    by_n = {r["n"]: r for r in target}
    d4, d8 = by_n[4.0], by_n[8.0]
    d_total = d8["Dmask_over_A"] - d4["Dmask_over_A"]
    d_core = d8["Dcore_over_A"] - d4["Dcore_over_A"]
    d_wall = d8["Dwall_over_A"] - d4["Dwall_over_A"]
    target_delta = [
        dict(from_n=4.0, to_n=8.0, delta_DA=d_total, delta_core=d_core, delta_wall=d_wall,
             core_fraction_of_rise=d_core / d_total, wall_fraction_of_rise=d_wall / d_total,
             core_share_of_DA_at_n8=d8["f_core"], wall_share_of_DA_at_n8=d8["f_wall"],
             core_share_of_DA_at_n4=d4["f_core"]),
    ]
    write_csv("core_target_delta_n4_to_n8.csv", target_delta)

    # -------- generalization --------
    gen_rows, n48_rows = [], []
    global LOW_HIGH_CACHE
    for N in (128, 256):
        for Re in (100, 500, 1000):
            for delta in (0.025, 0.05):
                sub = sorted((r for r in rows if int(r["N"]) == N and int(r["Re"]) == Re
                              and abs(r["delta_over_Lc"] - delta) < 1e-12),
                             key=lambda r: r["n"])
                if not sub:
                    continue
                LOW_HIGH_CACHE = sub
                nmin_row = min(sub, key=lambda r: r["Dmask_over_A"])
                nmax_row = max(sub, key=lambda r: r["n"])
                note = ""
                if nmax_row["n"] > nmin_row["n"]:
                    gen_rows.append(delta_row(nmin_row, nmax_row,
                                              "sampled_min_to_max_n"))
                else:
                    note = "no rise interval: sampled minimum is the largest available n"
                byn = {r["n"]: r for r in sub}
                if 4.0 in byn and 8.0 in byn:
                    n48_rows.append(delta_row(byn[4.0], byn[8.0], "n4_to_n8"))
                else:
                    n48_rows.append(dict(Re=Re, N=N, delta_over_Lc=delta,
                                         comparison="n4_to_n8",
                                         n_low=4.0 if 4.0 in byn else "",
                                         n_high=8.0 if 8.0 in byn else "",
                                         n_grid=",".join(f"{x:g}" for x in byn),
                                         unavailable="n=4" if 4.0 not in byn else "n=8",
                                         valid_rise=False, core_dominates=None))
    write_csv("core_generalization.csv", gen_rows)
    write_csv("core_n4_to_n8.csv", n48_rows)

    # -------- report --------
    L = [
        "# Additive core/wall budget: verification and qualified generalization",
        "",
        "Input: `corrections for reviewer/04_additive_core_wall_budget/core_wall_budget.csv` (506 rows, 253 cases x 2 band widths).",
        "Script: `corrections for reviewer/07_final_scientific_revision/analyze_core_wall.py`.",
        "",
        "Integrity checks: 506 unique (n,Re,N,delta) rows, 253 unique cases, "
        f"max |D_mask-(D_wall+D_core)| = {max(abs(r['additivity_residual']) for r in rows):.3g}.",
        "",
        "## Exact requested case: Re=1000, N=256, delta=0.05 L_c",
        "",
        "| n | D/A_mask | wall/A_mask | core/A_mask | wall share | core share |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for r in tgt_rows:
        L.append(f"| {r['n']:g} | {r['DA']:.6f} | {r['wall']:.6f} | {r['core']:.6f} | "
                 f"{r['f_wall']*100:.1f}% | {r['f_core']*100:.1f}% |")
    td = target_delta[0]
    L += [
        "",
        f"Delta n=4 -> 8: D/A_mask {d4['Dmask_over_A']:.6f} -> {d8['Dmask_over_A']:.6f} "
        f"(+{d_total:.6f}, +{d_total/d4['Dmask_over_A']*100:.2f}%); "
        f"core/A_mask +{d_core:.6f} ({td['core_fraction_of_rise']*100:.2f}% of the rise), "
        f"wall/A_mask +{d_wall:.6f} ({td['wall_fraction_of_rise']*100:.2f}%). "
        "The 88% figure is the **core fraction of the increase**, not the core share of D/A "
        f"(which is {d8['f_core']*100:.1f}% at n=8).",
        "",
        "## Generalization (Re=100, 500, 1000; N=128/256; delta=0.025/0.05)",
        "",
        "Definition used: `n_low` = sampled argmin of D/A_mask on the available n grid; "
        "`n_high` = largest available n (8 when present). "
        "`core_fraction = (core/A(n_high)-core/A(n_low))/(D/A(n_high)-D/A(n_low))`; "
        "core 'dominates' when this fraction > 50% and the total rise is positive.",
        "",
        "| Re | N | delta/Lc | n grid | n_low | n_high | D/A rise | core rise | core fraction | dominant? |",
        "|---:|---:|---:|---|---:|---:|---:|---:|---:|---|",
    ]
    for r in gen_rows:
        grids = sorted({x["n"] for x in rows if int(x["N"]) == r["N"] and int(x["Re"]) == r["Re"]
                        and abs(x["delta_over_Lc"] - r["delta_over_Lc"]) < 1e-12})
        L.append(f"| {r['Re']} | {r['N']} | {r['delta_over_Lc']:.3f} | "
                 f"{','.join(f'{x:g}' for x in grids)} | {r['n_low']:g} | {r['n_high']:g} | "
                 f"{r['delta_DA']:+.6f} | {r['delta_core']:+.6f} | "
                 f"{r['core_fraction_of_rise']*100:.1f}% | "
                 f"{'YES' if r['core_dominates'] else 'NO'} |")
    L += [
        "",
        "### Fixed n=4 -> n=8 comparison (where both exponents exist)",
        "",
        "| Re | N | delta/Lc | D/A rise | core rise | core fraction | dominant? |",
        "|---:|---:|---:|---:|---:|---:|---|",
    ]
    for r in n48_rows:
        if "delta_DA" in r:
            L.append(f"| {r['Re']} | {r['N']} | {r['delta_over_Lc']:.3f} | "
                     f"{r['delta_DA']:+.6f} | {r['delta_core']:+.6f} | "
                     f"{r['core_fraction_of_rise']*100:.1f}% | "
                     f"{'YES' if r['core_dominates'] else 'NO'} |")
        else:
            L.append(f"| {r['Re']} | {r['N']} | {r['delta_over_Lc']:.3f} | "
                     f"n/a ({r.get('unavailable','')} absent; grid {r['n_grid']}) | n/a | n/a | n/a |")
    L += [
        "",
        "### Caveats",
        "",
        "1. The n grids are uneven. N=128 uses the 10-point reference grid "
        "{1.25,1.5,1.75,2,2.5,3,4,5,6,8}; N=256 uses 17 exponents at Re=300/500/1000 "
        "and only n={2.5,3,4} at Re=100. A 'sampled minimum' is therefore a property of "
        "that grid, not an optimized continuous minimum.",
        "2. At Re=100, N=256, n=8 is absent; the only N=256 Re=100 exponents are 2.5, 3 and 4. "
        "No n=4->8 statement can be made there.",
        "3. Absolute D/A levels are not grid-converged (e.g. Re=1000,n=4,delta=0.025: "
        "0.007144 at N=128 vs 0.008797 at N=256), so every fraction above is a statement "
        "about the archived grids and the specified band width only.",
        "4. The denominator is always A_mask, never A_core or the exact A(n). "
        "Wall/core shares change with delta; only the additive identity is delta-independent.",
        "5. A 'core fraction of the rise' above 100% (e.g. Re=100,N=256 and Re=1000,N=256 "
        "in the sampled-min-to-max table) means the wall term decreases while the total "
        "rise stays positive. It is not a share of D/A and cannot exceed 100% in that sense.",
        "",
        "## Outputs",
        "",
        "* `core_target_Re1000_N256_d005.csv`, `core_target_delta_n4_to_n8.csv`, "
        "`core_generalization.csv`, `core_n4_to_n8.csv`.",
    ]
    (HERE / "core_wall_generalization.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"rows={len(rows)} maxres={max(abs(r['additivity_residual']) for r in rows):.3g}")
    print(f"n4->8 core fraction={td['core_fraction_of_rise']*100:.4f}% "
          f"wall fraction={td['wall_fraction_of_rise']*100:.4f}%")
    for r in gen_rows:
        print("GEN", r["Re"], r["N"], r["delta_over_Lc"], "nmin", r["n_low"],
              "nmax", r["n_high"], "rise", f"{r['delta_DA']:+.6f}",
              "corefrac", f"{r['core_fraction_of_rise']*100:.2f}%")


if __name__ == "__main__":
    main()
