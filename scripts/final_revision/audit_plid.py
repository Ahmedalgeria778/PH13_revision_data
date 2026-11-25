# -*- coding: utf-8 -*-
"""Audit whether archived LBM fields can support a reliable P_lid.

Read-only inputs: 05_dataset/**/*.npz and selected source/diagnostic files.
Outputs are written only to this directory.

Run:
  C:\\Users\\user\\AppData\\Local\\Programs\\Python\\Python314\\python.exe audit_plid.py
"""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
DATA = ROOT / "05_dataset"
SRC_PU = ROOT / "06_physics" / "analyse_etape4_puissance.py"
SRC_OBS = ROOT / "06_neural_operator" / "physics_observables.py"
SRC_MRT = ROOT / "02_LBM" / "mrt_collision.py"
ETS_CSV = ROOT / "06_physics" / "results_puissance" / "etape4_puissance.csv"
JB_REPORT = HERE.parent / "02_junction_energy_budget" / "junction_budget_report.md"
JB_IDENTITY = HERE.parent / "02_junction_energy_budget" / "identity_check.csv"


def rel(p: Path) -> str:
    try:
        return p.relative_to(ROOT).as_posix()
    except ValueError:
        return p.as_posix()


def write_csv(name: str, rows: list[dict]) -> None:
    if not rows:
        return
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with (HERE / name).open("w", encoding="utf-8", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=fields)
        wr.writeheader()
        wr.writerows(rows)


def main() -> None:
    files = sorted(DATA.rglob("*.npz"))
    per_file, by_dataset = [], defaultdict(lambda: {
        "final": 0, "checkpoint": 0, "final_with_f": 0,
        "checkpoint_with_f_it": 0, "final_keys": Counter(),
        "checkpoint_keys": Counter(), "examples": {},
    })
    for p in files:
        role = "checkpoint" if "_ckpt" in p.stem else "final"
        dataset = p.relative_to(DATA).parts[0] if p.is_relative_to(DATA) else "unknown"
        try:
            with np.load(p, allow_pickle=False) as z:
                keys = tuple(sorted(z.files))
        except Exception as exc:  # pragma: no cover - diagnostic only
            per_file.append(dict(dataset=dataset, role=role, path=rel(p),
                                 keys="ERROR", has_f="ERROR", has_f_it="ERROR",
                                 has_rho_ux_uy="ERROR", error=f"{type(exc).__name__}: {exc}"))
            continue
        has_f = "f" in keys
        has_f_it = has_f and "it" in keys
        has_rho_ux_uy = {"rho", "ux", "uy"}.issubset(keys)
        per_file.append(dict(dataset=dataset, role=role, path=rel(p),
                             keys="|".join(keys), has_f=has_f, has_f_it=has_f_it,
                             has_rho_ux_uy=has_rho_ux_uy, error=""))
        d = by_dataset[dataset]
        d[role] += 1
        if role == "final" and has_f:
            d["final_with_f"] += 1
        if role == "checkpoint" and has_f_it:
            d["checkpoint_with_f_it"] += 1
        d[f"{role}_keys"]["|".join(keys)] += 1
        d["examples"].setdefault((role, "|".join(keys)), rel(p))

    summary = []
    for dataset in sorted(by_dataset):
        d = by_dataset[dataset]
        summary.append(dict(
            dataset=dataset, final_fields=d["final"], checkpoints=d["checkpoint"],
            final_with_f=d["final_with_f"],
            checkpoint_with_f_and_it=d["checkpoint_with_f_it"],
            final_key_patterns=" ;; ".join(f"{k} (n={v})" for k, v in sorted(d["final_keys"].items())),
            checkpoint_key_patterns=" ;; ".join(f"{k} (n={v})" for k, v in sorted(d["checkpoint_keys"].items())),
            example_final=next((v for (role, _), v in d["examples"].items() if role == "final"), ""),
            example_checkpoint=next((v for (role, _), v in d["examples"].items() if role == "checkpoint"), ""),
        ))
    write_csv("plid_npz_inventory.csv", per_file)
    write_csv("plid_dataset_summary.csv", summary)

    # Representative rho convention, read from an archived final field.
    rep = DATA / "data_all190" / "se_n4p0_Re1000_N128.npz"
    rho_stats = {}
    with np.load(rep, allow_pickle=False) as z:
        rho = np.asarray(z["rho"], float)
        ux = np.asarray(z["ux"], float)
        uy = np.asarray(z["uy"], float)
        fluid = np.asarray(z["fluid"])
        mask = fluid > 0
        p_t = (rho - 1.0) / (3.0 * 0.05 ** 2)
        rho_stats = dict(
            path=rel(rep), N=int(z["N"]), n=float(z["n"]), Re=float(z["Re"]),
            fluid_cells=int(mask.sum()),
            rho_min=float(rho[mask].min()), rho_max=float(rho[mask].max()),
            rho_mean=float(rho[mask].mean()),
            p_from_rho_min=float(p_t[mask].min()), p_from_rho_max=float(p_t[mask].max()),
            ux_max=float(np.abs(ux[mask]).max()), uy_max=float(np.abs(uy[mask]).max()),
        )

    source_facts = [
        dict(item="MEM lid power formula", source=rel(SRC_PU), lines="15-17",
             fact="P_lid = sum_links (e_q . u_wall) * (f_new[q] + f_post[opp]); requires f_post and f_new on moving-wall links."),
        dict(item="Final fields lack f", source=rel(SRC_PU), lines="26-28",
             fact="Production script states that final .npz fields do not store f; N=256/512 use checkpoints, N=64/128 are re-run."),
        dict(item="Checkpoint fallback", source=rel(SRC_PU), lines="148-157",
             fact="get_f(N) reads z['f'] and z['it'] from *_ckpt.npz, otherwise runs CurvedLBM from scratch."),
        dict(item="One MEM step", source=rel(SRC_PU), lines="170-172",
             fact="rho,ux,uy = macroscopic(f); f_post = collide(f,S,fluid); stream_force(f_post,la,rho) yields P_lid."),
        dict(item="rho convention", source=rel(SRC_MRT), lines="64-69",
             fact="rho = f.sum(axis=0), ux = sum(e_x f)/rho, uy = sum(e_y f)/rho; p=(rho-1)/(3 U_lid^2) is in physics_observables.py:327."),
        dict(item="Stress lid power", source=rel(SRC_OBS), lines="325-337",
             fact="Alternative post-processing reconstructs du_t/dn and pressure-strain from archived (rho,u); this is an estimate, not MEM."),
        dict(item="Discrete identity failure", source=rel(JB_REPORT), lines="60-70",
             fact="On n=4, Re=1000, N=128: int(div F)/(-int 2phi) = -4.419 (expected +1); required pressure scale = -0.0783 (expected +1). Archived (rho,u) do not satisfy the discrete identity."),
    ]
    write_csv("plid_source_facts.csv", source_facts)

    with ETS_CSV.open("r", encoding="utf-8", newline="") as fh:
        est = list(csv.DictReader(fh))
    for r in est:
        r["provenance_note"] = "Requires f from checkpoint or re-run; NOT reconstructible from final (rho,ux,uy) alone."
    write_csv("plid_existing_estimates.csv", est)

    with JB_IDENTITY.open("r", encoding="utf-8", newline="") as fh:
        ident = {r["quantity"]: r["value"] for r in csv.DictReader(fh)}

    final_total = sum(s["final_fields"] for s in summary)
    final_f_total = sum(s["final_with_f"] for s in summary)
    ckpt_total = sum(s["checkpoints"] for s in summary)
    ckpt_f_it_total = sum(s["checkpoint_with_f_and_it"] for s in summary)

    L = [
        "# Can archived fields support a reliable P_lid?",
        "",
        "Script: `corrections for reviewer/07_final_scientific_revision/audit_plid.py`.",
        "",
        "## Verdict",
        "",
        "**No, not from the archived final fields alone.** A reliable production `P_lid` is the",
        "MEM link-sum `(e_q·u_wall)(f_new[q]+f_post[o])`. Final fields store only",
        "`rho, ux, uy, fluid, X, Y` plus metadata: no `f`, hence no `f_post`, no `f_new`, and",
        "no same-step boundary populations. `P_lid` can be computed only by instrumenting the",
        "solver, using a checkpoint that contains `f,it`, or re-running the case.",
        "",
        f"Inventory: {final_total} final `.npz` files under `05_dataset`, of which {final_f_total}",
        f"contain `f`; {ckpt_total} checkpoint files, of which {ckpt_f_it_total} contain both `f` and `it`.",
        "Per-dataset counts and exact key patterns are in `plid_dataset_summary.csv`; the full",
        "file-by-file inventory is in `plid_npz_inventory.csv`.",
        "",
        "## Source-level evidence",
        "",
    ]
    for f in source_facts:
        L.append(f"* `{f['source']}` lines {f['lines']}: {f['fact']}")
    L += [
        "",
        "## Representative archived final field (rho convention)",
        "",
        f"`{rho_stats['path']}`: n={rho_stats['n']:g}, Re={rho_stats['Re']:g}, N={rho_stats['N']},",
        f"{rho_stats['fluid_cells']} fluid cells. On fluid cells: rho in",
        f"[{rho_stats['rho_min']:.6g}, {rho_stats['rho_max']:.6g}], mean {rho_stats['rho_mean']:.6g};",
        "with `U_lid=0.05`, `p=(rho-1)/(3U_lid^2)` spans",
        f"[{rho_stats['p_from_rho_min']:.6g}, {rho_stats['p_from_rho_max']:.6g}].",
        "This pressure is only a post-processing convention applied to an archived rho field;",
        "it does not restore the populations needed by MEM.",
        "",
        "## Why the stress-based reconstruction is not a substitute",
        "",
        "`physics_observables.py:325` computes `lid_power = 2*nu*sum(du_t/dn ds)` from the",
        "near-wall velocity, and lines 326-337 compute pressure-strain forces from `p` and `S`.",
        "Both use archived time-averaged macroscopic fields and a sampled wall location. The",
        "independent discrete identity test on `n=4, Re=1000, N=128` gives:",
        f"`int(div F)/(-int 2phi)` = `{ident['ratio']}` (expected +1) and required pressure scale",
        f"`{ident['required_pressure_scale']}` (expected +1). Therefore the flux built from",
        "archived `(rho,u)` is not a verified energy balance, and it cannot be used to claim",
        "that `P_lid=D`.",
        "",
        "## Existing P_lid numbers and their provenance",
        "",
        "The only archived `P_lid` series (`06_physics/results_puissance/etape4_puissance.csv`)",
        "was produced from `f` in checkpoints or from fresh runs, not from final fields:",
        "",
        "| N | source_f | it | P_lid | P/Phi |",
        "|---:|---|---:|---:|---:|",
    ]
    for r in est:
        src = r["source_f"]
        if len(src) > 60:
            src = "..." + src[-57:]
        L.append(f"| {r['N']} | {src} | {int(float(r['it']))} | {float(r['P_lid']):.6e} | "
                 f"{float(r['P_over_Phi']):.3f} |")
    L += [
        "",
        "The series increases with N and `P/Phi` is not unity, so it must not be presented as",
        "a grid-converged or verified global power balance.",
        "",
        "## Outputs",
        "",
        "* `plid_npz_inventory.csv`, `plid_dataset_summary.csv`, `plid_source_facts.csv`,",
        "`plid_existing_estimates.csv`, `plid_audit_report.md`.",
    ]
    (HERE / "plid_audit_report.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"final={final_total} with_f={final_f_total} checkpoints={ckpt_total} "
          f"ckpt_with_f_it={ckpt_f_it_total}")
    for s in summary:
        print(f"{s['dataset']:24s} final={s['final_fields']:4d} f={s['final_with_f']:3d} "
              f"ckpt={s['checkpoints']:4d} f_it={s['checkpoint_with_f_and_it']:4d}")


if __name__ == "__main__":
    main()
