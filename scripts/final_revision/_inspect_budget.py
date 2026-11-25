import csv
from pathlib import Path

p = Path(r"C:\Users\user\Documents\Default Project\GIRVD (revised)\corrections for reviewer\04_additive_core_wall_budget\core_wall_budget.csv")
with p.open("r", encoding="utf-8-sig", newline="") as fh:
    rows = list(csv.DictReader(fh))
print("rows", len(rows))
print("fields", list(rows[0]))
print("first", rows[0])
print("case_id", len(set(r["case_id"] for r in rows)))
print("n_Re_N", len(set((r["n"], r["Re"], r["N"]) for r in rows)))
print("case_delta", len(set((r["case_id"], r["delta_over_Lc"]) for r in rows)))
print("N_Re_delta", len(set((r["N"], r["Re"], r["delta_over_Lc"]) for r in rows)))
