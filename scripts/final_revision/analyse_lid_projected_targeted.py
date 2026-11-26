# -*- coding: utf-8 -*-
"""Analyse the targeted projected-lid control fields.

The reference law is tangential, u_w = U_lid t.  The projected control uses the
impermeable horizontal intent u_w = U_lid (e_x.t) t.  This script compares the
two laws on the exact requested design:

    N=128: n=1.5,2,4,8 at Re=100 and 1000;
    N=256: n=1.5,2,4,8 at Re=1000 and n=4 at Re=100.

Two N=128/Re=1000 projected fields (n=2,4,8) are reused from the earlier
control archive; all other projected fields come from data_lid_projected_targeted.

Outputs are written to 06_physics/results_lid_projected_targeted; the table
fragment (including the forcing-normalized dissipation ratio) is copied to the
submission package root and the figure files are copied into its figs_new folder.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from scipy import ndimage  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for p in (str(HERE), str(ROOT / "01_geometry")):
    if p not in sys.path:
        sys.path.insert(0, p)

from etude_convergence_paroi import gradient_valid_mask  # noqa: E402

DATA = ROOT / "05_dataset"
TANGENT = DATA / "data_all190"
CONV256 = DATA / "data_conv256"
LOWRE256 = DATA / "data_conv256_lowRe"
PROJ_NEW = DATA / "data_lid_projected_targeted"
PROJ_OLD = DATA / "data_lid_projected"
OUT = HERE / "results_lid_projected_targeted"
PKG_FIGS = ROOT / "08_operator_results" / "PH13_manuscript" / "submission_package" / "figs_new"
PKG = PKG_FIGS.parent

DESIGN = tuple(
    (n, re, N)
    for N, res in ((128, (100.0, 1000.0)), (256, (100.0, 1000.0)))
    for re in res
    for n in ((4.0,) if (N == 256 and re == 100.0) else (1.5, 2.0, 4.0, 8.0))
)


def cid(n: float, re: float, N: int) -> str:
    return f"se_n{str(round(n, 2)).replace('.', 'p')}_Re{int(round(re))}_N{N}"


def projected_path(n: float, re: float, N: int) -> Path:
    new = PROJ_NEW / f"{cid(n, re, N)}_proj.npz"
    if new.exists() or N != 128:
        return new
    return PROJ_OLD / f"{cid(n, re, 128)}_proj.npz"


def tangential_path(n: float, re: float, N: int) -> Path:
    if N == 128:
        return TANGENT / f"{cid(n, re, 128)}.npz"
    if N == 256 and re == 100.0:
        return LOWRE256 / f"{cid(n, re, 256)}.npz"
    return CONV256 / f"{cid(n, re, 256)}.npz"


def load(path: Path) -> dict:
    with np.load(path) as d:
        ux = np.asarray(d["ux"], dtype=float)
        uy = np.asarray(d["uy"], dtype=float)
        fluid = np.asarray(d["fluid"]).astype(bool)
        xx = np.asarray(d["X"], dtype=float)
        yy = np.asarray(d["Y"], dtype=float)
        dx = float(abs(xx[0, 1] - xx[0, 0]))
        out = {
            "path": str(path),
            "n": float(d["n"]),
            "Re": float(d["Re"]),
            "N": int(d["N"]),
            "ux": ux,
            "uy": uy,
            "fluid": fluid,
            "dx": dx,
            "area_exact": float(d["area_exact"]),
            "L_char": float(d["L_char"]),
            "iters": int(d["iters_lbm"]),
            "residual": float(d["residual_lbm"]),
        }
        meta = str(d["_meta"]) if "_meta" in d.files else ""
    if meta:
        try:
            out["lid"] = json.loads(meta).get("lid_velocity", "tangential")
        except json.JSONDecodeError:
            out["lid"] = "unknown"
    else:
        out["lid"] = "tangential"
    return out


def diagnostics(d: dict) -> dict:
    ux, uy, fluid, dx = d["ux"], d["uy"], d["fluid"], d["dx"]
    re = d["Re"]
    valid = gradient_valid_mask(fluid)
    ux_x = np.full(ux.shape, np.nan)
    uy_x = np.full(ux.shape, np.nan)
    ux_y = np.full(ux.shape, np.nan)
    uy_y = np.full(ux.shape, np.nan)
    ux_x[1:-1, 1:-1] = (ux[1:-1, 2:] - ux[1:-1, :-2]) / (2.0 * dx)
    uy_x[1:-1, 1:-1] = (uy[1:-1, 2:] - uy[1:-1, :-2]) / (2.0 * dx)
    ux_y[1:-1, 1:-1] = (ux[2:, 1:-1] - ux[:-2, 1:-1]) / (2.0 * dx)
    uy_y[1:-1, 1:-1] = (uy[2:, 1:-1] - uy[:-2, 1:-1]) / (2.0 * dx)
    for arr in (ux_x, uy_x, ux_y, uy_y):
        arr[~valid] = np.nan
    s_ss = 2.0 * ux_x ** 2 + 2.0 * uy_y ** 2 + (ux_y + uy_x) ** 2
    phi = np.where(valid, s_ss / re, 0.0)
    cell = dx * dx
    D = 2.0 * float(np.sum(phi)) * cell
    A_mask = float(np.count_nonzero(valid)) * cell
    KE = 0.5 * float(np.sum(np.where(fluid, ux ** 2 + uy ** 2, 0.0))) * cell
    dist_cells = ndimage.distance_transform_edt(fluid)
    l_c = d["L_char"] * dx
    shares = {}
    for frac in (0.025, 0.05, 0.25):
        band = valid & (dist_cells * dx <= frac * l_c)
        shares[f"f{frac:g}"] = (2.0 * float(np.sum(np.where(band, phi, 0.0))) * cell / D)
    return {
        "D": D,
        "A_mask": A_mask,
        "D_A_mask": D / A_mask,
        "KE_A_exact": KE / d["area_exact"],
        "umax": float(np.hypot(ux[fluid], uy[fluid]).max()),
        **shares,
    }


def rel_l2(p: dict, t: dict) -> tuple[float, float]:
    common = p["fluid"] & t["fluid"]
    du = p["ux"][common] - t["ux"][common]
    ut = t["ux"][common], t["uy"][common]
    num = float(np.sqrt(np.mean(du ** 2 + (p["uy"][common] - t["uy"][common]) ** 2)))
    den = float(np.sqrt(np.mean(ut[0] ** 2 + ut[1] ** 2)))
    return num / den, num / float(np.hypot(*ut).max())


def make_table(rows: list[dict]) -> str:
    header = r"""\begin{tabular}{@{}rrrcccccccr@{}}
\toprule
$N$ & $Re$ & $n$ & $D/A_{\rm mask}$ tan. & $D/A_{\rm mask}$ proj. & raw ratio &
forcing-norm.\ ratio & $KE/A$ ratio & $f_{0.25}$ ratio & $U_{\max}$ ratio & rel. $L_2(u)$ \\
\midrule
"""
    body = []
    for r in rows:
        body.append(
            f"{r['N']:d} & {r['Re']:.0f} & {r['n']:.1f} & "
            f"{r['DA_tan']:.5f} & {r['DA_proj']:.5f} & {r['DA_ratio']:.3f} & "
            f"{r['DA_ratio_norm']:.3f} & {r['KE_ratio']:.3f} & "
            f"{r['f025_ratio']:.3f} & {r['umax_ratio']:.3f} & {r['relL2']:.3f} \\\\"
        )
    return header + "\n".join(body) + "\n" + r"\bottomrule" + "\n" + r"\end{tabular}" + "\n"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    PKG_FIGS.mkdir(parents=True, exist_ok=True)
    rows = []
    missing = []
    for n, re, N in DESIGN:
        pp, tp = projected_path(n, re, N), tangential_path(n, re, N)
        if not (pp.exists() and tp.exists()):
            missing.append((n, re, N, str(pp), str(tp)))
            continue
        p, t = load(pp), load(tp)
        dp, dt = diagnostics(p), diagnostics(t)
        rel, rel_umax = rel_l2(p, t)
        rows.append({
            "N": N, "Re": re, "n": n,
            "DA_tan": dt["D_A_mask"], "DA_proj": dp["D_A_mask"],
            "DA_ratio": dp["D_A_mask"] / dt["D_A_mask"],
            "DA_ratio_norm": (dp["D_A_mask"] / dt["D_A_mask"]) / 0.5,
            "KE_tan": dt["KE_A_exact"], "KE_proj": dp["KE_A_exact"],
            "KE_ratio": dp["KE_A_exact"] / dt["KE_A_exact"],
            "f025_tan": dt["f0.025"], "f025_proj": dp["f0.025"],
            "f025_ratio": dp["f0.025"] / dt["f0.025"],
            "f05_tan": dt["f0.05"], "f05_proj": dp["f0.05"],
            "umax_tan": dt["umax"], "umax_proj": dp["umax"],
            "umax_ratio": dp["umax"] / dt["umax"],
            "relL2": rel, "relL2_umax": rel_umax,
            "iters_tan": t["iters"], "iters_proj": p["iters"],
            "res_tan": t["residual"], "res_proj": p["residual"],
            "path_tan": tp.as_posix(), "path_proj": pp.as_posix(),
            "lid_proj": p["lid"],
        })
    if missing:
        print("[targeted-analysis] missing fields:")
        for item in missing:
            print("  ", item)
        return 2

    with (OUT / "table.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    table_tex = make_table(rows)
    (OUT / "projected_lid_table.tex").write_text(table_tex, encoding="utf-8")
    (PKG / "projected_lid_table.tex").write_text(table_tex, encoding="utf-8")

    shape = {}
    for N in (128, 256):
        for re in (100.0, 1000.0):
            sub = [r for r in rows if r["N"] == N and r["Re"] == re]
            if len(sub) < 3:
                continue
            ref = min(r["n"] for r in sub)
            s = {}
            for law in ("tan", "proj"):
                vals = {r["n"]: r[f"DA_{law}"] / next(
                    x[f"DA_{law}"] for x in sub if x["n"] == ref) for r in sub}
                nmin = min(vals, key=vals.get)
                depth = 100.0 * (1.0 - vals[nmin])
                s[law] = {"argmin_sampled": nmin, "depth_pct": depth,
                          "shape": vals}
            s["max_abs_shape_diff"] = max(
                abs(s["tan"]["shape"][n] - s["proj"]["shape"][n])
                for n in s["tan"]["shape"])
            shape[f"N{N}_Re{int(re)}"] = s
    synth = {
        "rows": rows, "shape": shape, "n_cases": len(rows),
        "convention": ("D=2 sum_{valid} (S:S/Re) dx^2; "
                       "A_mask=count(valid) dx^2; KE/A uses A_exact"),
        "controls": ("coupled geometry/forcing control; no causal isolation "
                     "of curvature, confinement or wall kinematics"),
        "boundary_velocity_integral_ratio": 0.5,
        "DA_ratio_raw_range": [min(r["DA_ratio"] for r in rows),
                               max(r["DA_ratio"] for r in rows)],
        "DA_ratio_forcing_normalized_range": [
            min(r["DA_ratio_norm"] for r in rows),
            max(r["DA_ratio_norm"] for r in rows),
        ],
        "KE_ratio_range": [min(r["KE_ratio"] for r in rows),
                           max(r["KE_ratio"] for r in rows)],
    }
    (OUT / "synthese.json").write_text(
        json.dumps(synth, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# Targeted projected-lid control", "",
        "Projected law: u_w = U_lid (e_x.t) t (impermeable); tangential law: "
        "u_w = U_lid t. Same n, Re, N and Mach number. D/A is divided by the "
        "gradient-valid integration area A_mask; KE/A uses the exact area.", "",
        "| N | Re | n | D/A tan | D/A proj | raw ratio | forcing-norm. ratio | "
        "KE/A ratio | f_0.25 ratio | umax ratio | relL2 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in rows:
        lines.append(
            f"| {r['N']} | {r['Re']:.0f} | {r['n']:.1f} | {r['DA_tan']:.5f} | "
            f"{r['DA_proj']:.5f} | {r['DA_ratio']:.3f} | {r['DA_ratio_norm']:.3f} | "
            f"{r['KE_ratio']:.3f} | {r['f025_ratio']:.3f} | "
            f"{r['umax_ratio']:.3f} | {r['relL2']:.3f} |")
    lines += ["", "## Geometry-relative shape, normalized by smallest sampled n", ""]
    for key, s in shape.items():
        lines.append(
            f"- {key}: sampled argmin {s['tan']['argmin_sampled']:g} (tan) vs "
            f"{s['proj']['argmin_sampled']:g} (proj); depth "
            f"{s['tan']['depth_pct']:.1f}% vs {s['proj']['depth_pct']:.1f}%; "
            f"max |difference| {s['max_abs_shape_diff']:.3f}.")
    (OUT / "rapport.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    fig, axes = plt.subplots(1, 3, figsize=(15.0, 4.2), constrained_layout=True)
    for ax, N in zip(axes[:2], (128, 256)):
        for re, ls in ((100.0, "-"), (1000.0, "--")):
            sub = [r for r in rows if r["N"] == N and r["Re"] == re]
            if not sub:
                continue
            ns = [r["n"] for r in sub]
            ax.plot(ns, [r["DA_tan"] for r in sub], ls, marker="o", ms=5,
                    lw=1.8, label=f"tangential, Re={re:.0f}")
            ax.plot(ns, [r["DA_proj"] for r in sub], ls, marker="s", ms=5,
                    lw=1.8, label=f"projected, Re={re:.0f}")
        ax.set_xscale("log", base=2)
        ax.set_yscale("log")
        ax.set_xticks([1.5, 2.0, 4.0, 8.0])
        ax.set_xticklabels(["1.5", "2", "4", "8"])
        ax.set_xlabel("superelliptic exponent $n$")
        ax.set_ylabel(r"$D/A_{\rm mask}$")
        ax.set_title(f"$N={N}$")
        ax.grid(alpha=0.25)
        ax.legend(fontsize=8, frameon=False)

    ax = axes[2]
    for N, marker in ((128, "o"), (256, "s")):
        for re, ls in ((100.0, "-"), (1000.0, "--")):
            sub = [r for r in rows if r["N"] == N and r["Re"] == re]
            if not sub:
                continue
            ax.plot([r["n"] for r in sub],
                    [r["DA_ratio_norm"] for r in sub], ls, marker=marker,
                    ms=5, lw=1.8,
                    label=f"$N={N}$, Re={re:.0f}")
    ax.axhline(1.0, color="0.35", lw=1.0, ls=":")
    ax.set_xscale("log", base=2)
    ax.set_xticks([1.5, 2.0, 4.0, 8.0])
    ax.set_xticklabels(["1.5", "2", "4", "8"])
    ax.set_xlabel("superelliptic exponent $n$")
    ax.set_ylabel("forcing-normalized ratio")
    ax.set_title(r"$D/A$ ratio / $\int u_{\rm lid}^2ds$ ratio")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=7.5, frameon=False)
    fig.suptitle("Tangential versus projected impermeable lid", fontsize=12)
    for ext in ("png", "pdf"):
        fig.savefig(OUT / f"fig_lid_projected_targeted.{ext}", dpi=220,
                    bbox_inches="tight")
        fig.savefig(PKG_FIGS / f"fig_lid_projected_targeted.{ext}", dpi=220,
                    bbox_inches="tight")
    plt.close(fig)

    print(f"[targeted-analysis] {len(rows)} cases compared")
    for key, s in shape.items():
        print(f"[targeted-analysis] {key}: argmin {s['tan']['argmin_sampled']:g}"
              f"->{s['proj']['argmin_sampled']:g}; depth "
              f"{s['tan']['depth_pct']:.1f}->{s['proj']['depth_pct']:.1f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
