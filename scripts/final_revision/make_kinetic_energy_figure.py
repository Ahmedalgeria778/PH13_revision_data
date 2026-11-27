"""Regenerate the integrated-kinetic-energy curve from the archived CSV.

The plotting function is imported from the canonical mapping analysis so that
the regenerated figure uses exactly the same samples and conventions as the
original 190-case deliverable.  The only intended change is the black-and-white
safe marker/line-style assignment in that function.
"""
from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[4]
MAPPING = ROOT / "05_dataset" / "data" / "analyse_physique_mapping.py"
CSV = ROOT / "06_physics" / "results_190" / "physics_observables.csv"
SOURCE = ROOT / "06_physics" / "results_190" / "curve_kinetic_energy_vs_n.png"
OUTS = [
    SOURCE,
    ROOT / "08_operator_results" / "PH13_manuscript" / "submission_package" / "figs_new",
    ROOT / "08_operator_results" / "PH13_manuscript" / "submission_package" / "figs",
    ROOT / "corrections for reviewer" / "PH13_revision_data" / "figures" / "final_supplement",
    ROOT / "corrections for reviewer" / "PH13_revision_data" / "supplement" / "figs_new",
    ROOT / "corrections for reviewer" / "PH13_revision_data" / "supplement" / "figs",
]

spec = importlib.util.spec_from_file_location("analyse_physique_mapping", MAPPING)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)

with CSV.open(newline="", encoding="utf-8") as fh:
    rows = [
        SimpleNamespace(
            n=float(r["n"]),
            Re=float(r["Re"]),
            kinetic_energy=float(r["kinetic_energy"]),
        )
        for r in csv.DictReader(fh)
    ]

mod._plot_curves(
    rows,
    "kinetic_energy",
    SOURCE,
    "Kinetic energy versus n",
    "Kinetic energy",
)
for out in OUTS:
    if out.is_dir():
        out.mkdir(parents=True, exist_ok=True)
        target = out / SOURCE.name
    else:
        target = out
        target.parent.mkdir(parents=True, exist_ok=True)
    if target != SOURCE:
        target.write_bytes(SOURCE.read_bytes())
    print("wrote", target)
