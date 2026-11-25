# -*- coding: utf-8 -*-
"""
06_physics/etude_corner_bnd.py

Chantier D — ANALYSE : couches limites de coin et onset de la corner eddy.

Etude LOCALE dediee aux coins de la ligne la plus sensible (n=8), en
reutilisant l'algorithme canonique de la campagne B (etude_convergence_paroi)
et la streamfunction canonique (analyse_physique_mapping) :

  * bande de coin : fraction de dissipation dans un rayon rho autour des 4
    coins de la boite englobante (rho/L_c in {0.10, 0.20}), et decomposition
    par coin. Le domaine superelliptique (n=8) est un carre ARRONDI : il
    n'atteint jamais les coins de la boite (distance minimale fluide->coin
    ~0.12 L_c/2), d'ou des rayons plus larges que la bande de mur. C'est la
    contribution INTERIEURE que la bande de mur (delta/L_c) ne resout pas
    (phrase de la section "Scope and limitations").
  * corner eddy : extrema de la streamfunction (min/max locaux), force
    |psi| du tourbillon secondaire de coin, position, taille (distance au
    coin le plus proche), comptes aux seuils canoniques 1/3/5 % (meme regle
    que le vortex_catalog).
  * convergence : ordre empirique et extrapolation de Richardson en N pour
    la fraction de coin et la force de la corner eddy (n=8 Re=1000 a
    N=64/128/256, N=512 est ajoute par la campagne).

Champs lus (aucune simulation ici) :
    n=8 a tous Re disponibles + N dispo (data_all190, data_conv, data_corner)
    n=3 Re=1000 N=64/128/256 (controle : aucun eddy de coin attendu)

Sorties (06_physics/results_corner/) : csv, md, json, png.
Re-lancement apres la campagne N=512 : meme script, ajoute le cas si present.
"""

from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np
from scipy import ndimage  # noqa: E402

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parent
for _p in (str(_ROOT / "05_dataset" / "data"),):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from etude_convergence_paroi import (  # noqa: E402
    Boundary, analyse_case, gradient_valid_mask, richardson,
)
from analyse_physique_mapping import solve_streamfunction  # noqa: E402

ALL190 = _ROOT / "05_dataset" / "data_all190"
CONV = _ROOT / "05_dataset" / "data_conv"
CORNER = _ROOT / "05_dataset" / "data_corner"
OUT_DIR = _HERE / "results_corner"

# rayons des bandes de coin, en fraction de L_c (le domaine arrondi n'atteint
# pas les coins de boite : distance fluide->coin ~0.06 L_c)
CORNER_RHO_LC = (0.10, 0.20)
EDDY_RADIUS_LC = 0.25
PCTS = (1, 3, 5)
# coins de la BOITE englobante (-1..1)^2 — sommets du carre arrondi
BOX_CORNERS = {"bl": (-1.0, -1.0), "br": (1.0, -1.0),
               "tl": (-1.0, 1.0), "tr": (1.0, 1.0)}

# diagnostics de convergence suivis pour le chantier coin
DIAGS = ("f_corner_pct20", "psi_corner_max", "size_corner")


def richardson_corner(q: dict[int, float], name: str) -> dict:
    """Richardson multi-niveaux sur TOUS les N dispo (64..512) pour le coin.

    richardson() de la campagne B est cable sur NS=(64,128,256) et ignore
    N=512 ; ici on traite une suite quelconque de N anc. Raffinement 2x
    uniforme (64,128,256,512) : h = 1/N, modele q0 + C*h**p.

    q : {N: valeur} deja filtre des non-finies.
    Retourne (interface proche de richardson) :
      values {N: v}, change_last (variation relative du dernier saut),
      plateau_1pct (change_last < 1 %), p_intervals (ordres par fenetre de
      3 points), order_p (ordre du dernier intervalle), q_extrap.
    """
    Ns = sorted(q)
    vals = [q[n] for n in Ns]
    out = {"name": name, "values": {n: q[n] for n in Ns},
           "change_last": None, "plateau_1pct": None,
           "p_intervals": [], "order_p": None, "q_extrap": None}
    if len(Ns) < 2:
        return out
    changes = [abs(vals[i + 1] - vals[i]) / abs(vals[i + 1])
               for i in range(len(vals) - 1) if vals[i + 1]]
    out["change_last"] = changes[-1] if changes else None
    out["plateau_1pct"] = bool(out["change_last"] is not None
                               and out["change_last"] < 0.01)
    if len(Ns) < 3:
        return out
    for i in range(len(vals) - 2):
        e1 = abs(vals[i + 1] - vals[i])
        e2 = abs(vals[i + 2] - vals[i + 1])
        if e1 > 1e-300 and e2 > 0 and e2 < e1:
            out["p_intervals"].append(math.log2(e1 / e2))
        else:
            out["p_intervals"].append(None)
    p = out["p_intervals"][-1] if out["p_intervals"] else None
    if p is not None and p > 0:
        out["order_p"] = p
        out["q_extrap"] = vals[-1] + (vals[-1] - vals[-2]) / (2.0 ** p - 1.0)
    return out


# ------------------------------------------------------------- champs ----
def find_cases():
    rows = []
    for d in (ALL190, CONV, CORNER):
        if not d.exists():
            continue
        for npz in d.glob("se_*.npz"):
            if "_ckpt" in npz.stem or "_tmp" in npz.stem:
                continue  # fichiers de reprise internes (f,it) — pas des champs
            with np.load(npz) as f:
                n = float(f["n"])
                Re = float(f["Re"])
                N = int(f["N"])
            keep = (abs(n - 8.0) < 1e-9) or (abs(n - 3.0) < 1e-9 and Re == 1000.0)
            if keep:
                rows.append({"path": str(npz), "n": n, "Re": Re, "N": N})
    rows.sort(key=lambda r: (r["n"], r["Re"], r["N"]))
    return rows


def dissipation_field(ux, uy, fluid, Re, dx):
    """Champ phi identique a la campagne B (etude_convergence_paroi)."""
    valid = gradient_valid_mask(fluid)
    ux_x = np.full(ux.shape, np.nan)
    uy_y = np.full(ux.shape, np.nan)
    ux_y = np.full(ux.shape, np.nan)
    uy_x = np.full(ux.shape, np.nan)
    ux_x[1:-1, 1:-1] = (ux[1:-1, 2:] - ux[1:-1, :-2]) / (2.0 * dx)
    uy_x[1:-1, 1:-1] = (uy[1:-1, 2:] - uy[1:-1, :-2]) / (2.0 * dx)
    ux_y[1:-1, 1:-1] = (ux[2:, 1:-1] - ux[:-2, 1:-1]) / (2.0 * dx)
    uy_y[1:-1, 1:-1] = (uy[2:, 1:-1] - uy[:-2, 1:-1]) / (2.0 * dx)
    for a in (ux_x, uy_x, ux_y, uy_y):
        a[~valid] = np.nan
    phi = (2.0 * ux_x ** 2 + 2.0 * uy_y ** 2 + (ux_y + uy_x) ** 2) / Re
    phi = np.where(valid, phi, 0.0)
    return phi, valid


def corner_distance_field(X, Y):
    """Distance de chaque cellule au coin de boite le plus proche."""
    d = np.full(X.shape, np.inf)
    for _k, (xc, yc) in BOX_CORNERS.items():
        d = np.minimum(d, np.hypot(X - xc, Y - yc))
    return d


def psi_extrema(psi, valid):
    size = 3
    mx = ndimage.maximum_filter(psi, size=size)
    mn = ndimage.minimum_filter(psi, size=size)
    maxs = (psi == mx) & (~np.isnan(psi)) & valid
    mins = (psi == mn) & (~np.isnan(psi)) & valid
    cands = []
    for ii, jj in zip(*np.nonzero(maxs)):
        cands.append({"i": int(ii), "j": int(jj), "psi": float(psi[ii, jj]),
                      "kind": "max"})
    for ii, jj in zip(*np.nonzero(mins)):
        cands.append({"i": int(ii), "j": int(jj), "psi": float(psi[ii, jj]),
                      "kind": "min"})
    return cands


def dist_to_any_corner(x, y, xx, yy):
    vx = np.array([v[0] for v in BOX_CORNERS.values()])
    vy = np.array([v[1] for v in BOX_CORNERS.values()])
    return float(np.min(np.hypot(x - vx, y - vy)))


def analyse_corner(path: Path, boundary: Boundary) -> dict:
    base = analyse_case(path, boundary)  # diagnostics canoniques B
    with np.load(path) as data:
        ux = np.asarray(data["ux"], dtype=float)
        uy = np.asarray(data["uy"], dtype=float)
        fluid = np.asarray(data["fluid"]).astype(bool)
        xx = np.asarray(data["X"], dtype=float)
        yy = np.asarray(data["Y"], dtype=float)
        Re = float(data["Re"])
    dx = float(abs(xx[0, 1] - xx[0, 0]))
    l_c = base["L_c"]
    out = {k: base[k] for k in ("case_id", "n", "Re", "N", "A", "D", "D_A",
                                "umax", "perimeter", "kappa_mean",
                                "f_delta_05")}
    out["L_c"] = l_c

    phi, valid = dissipation_field(ux, uy, fluid, Re, dx)
    d_cell = corner_distance_field(xx, yy)

    # bandes de coin (totales) et decomposition par coin (rayon max)
    for _rho_f in CORNER_RHO_LC:
        key = f"f_corner_pct{int(round(_rho_f * 100)):02d}"
        rho = _rho_f * l_c
        band = valid & (d_cell <= rho)
        d_band = 2.0 * float(np.sum(np.where(band, phi, 0.0))) * dx * dx
        out[key] = d_band / base["D"] if base["D"] > 0 else float("nan")
    rho_max = max(CORNER_RHO_LC) * l_c
    for name, (xc, yc) in BOX_CORNERS.items():
        dk = np.hypot(xx - xc, yy - yc)
        band = valid & (dk <= rho_max)
        d_band = 2.0 * float(np.sum(np.where(band, phi, 0.0))) * dx * dx
        out[f"fcorner_{name}"] = d_band / base["D"] if base["D"] > 0 else \
            float("nan")

    # streamfunction + extrema + corner eddy
    om = np.full(ux.shape, 0.0)
    om[1:-1, 1:-1] = ((uy[1:-1, 2:] - uy[1:-1, :-2])
                      - (ux[2:, 1:-1] - ux[:-2, 1:-1])) / (2.0 * dx)
    om[~valid] = 0.0
    psi = solve_streamfunction(om, fluid, dx, dx)
    cands = psi_extrema(psi, valid & ~np.isnan(psi))
    out["n_extrema_raw"] = len(cands)
    if not cands:
        out["n_vortex_p1"] = 0
        out["n_vortex_p3"] = 0
        out["n_vortex_p5"] = 0
        out["psi_primary"] = float("nan")
        out["psi_corner_max"] = float("nan")
        out["x_corner"] = float("nan")
        out["y_corner"] = float("nan")
        out["size_corner"] = float("nan")
        return out

    cands.sort(key=lambda c: -abs(c["psi"]))
    psi_primary = cands[0]["psi"]
    out["psi_primary"] = psi_primary

    for pct in PCTS:
        thr = pct / 100.0 * abs(psi_primary)
        out[f"n_vortex_p{pct}"] = sum(
            1 for c in cands[1:] if abs(c["psi"]) >= thr)

    # tourbillon secondaire de coin : plus fort extremum hors primaire situe
    # a moins de EDDY_RADIUS_LC * L_c d'un coin de la boite
    r_eddy = EDDY_RADIUS_LC * l_c
    eddies = []
    for c in cands[1:]:
        dk = dist_to_any_corner(float(xx[c["i"], c["j"]]),
                                float(yy[c["i"], c["j"]]), xx, yy)
        if dk <= r_eddy:
            eddies.append({**c, "dist_corner": dk})
    if eddies:
        e = max(eddies, key=lambda c: abs(c["psi"]))
        out["psi_corner_max"] = e["psi"]
        out["x_corner"] = float(xx[e["i"], e["j"]])
        out["y_corner"] = float(yy[e["i"], e["j"]])
        out["size_corner"] = e["dist_corner"]
    else:
        out["psi_corner_max"] = float("nan")
        out["x_corner"] = float("nan")
        out["y_corner"] = float("nan")
        out["size_corner"] = float("nan")
    return out


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cases = find_cases()
    rows = []
    for c in cases:
        n, Re, N = c["n"], c["Re"], c["N"]
        try:
            bnd = Boundary(n)
            row = analyse_corner(Path(c["path"]), bnd)
            rows.append(row)
            print(f"[corner-ana] {row['case_id']} "
                  f"D_A={row['D_A']:.4e} fcorner_pct20={row['f_corner_pct20']:.4f} "
                  f"n_v1={row['n_vortex_p1']} "
                  f"psi_eddy={row['psi_corner_max']:.3e}", flush=True)
        except Exception as exc:  # noqa: BLE001
            print(f"[corner-ana] ECHEC {c['path']}: {exc!r}", flush=True)

    # ---------- csv
    fields = ["case_id", "n", "Re", "N", "D_A", "f_corner_pct10",
              "f_corner_pct20", "fcorner_tl", "fcorner_tr", "fcorner_bl",
              "fcorner_br", "n_vortex_p1", "n_vortex_p3", "n_vortex_p5",
              "psi_corner_max", "x_corner", "y_corner", "size_corner"]
    with (OUT_DIR / "corner_bnd.csv").open("w", newline="",
                                           encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in sorted(rows, key=lambda r: (r["n"], r["Re"], r["N"])):
            w.writerow(r)

    # ---------- convergence (Richardson) par (n, Re)
    groups = {}
    for r in rows:
        groups.setdefault((r["n"], r["Re"]), {})[r["N"]] = r
    conv = []
    for (n, Re), byN in sorted(groups.items()):
        if len(byN) < 2:
            continue
        for d in DIAGS:
            q = {N_: byN[N_][d] for N_ in byN if byN[N_][d] == byN[N_][d]}
            if len(q) >= 2:
                rch = richardson_corner(q, d)
                conv.append({"n": n, "Re": Re, "diag": d,
                             **{f"N{k}": rch["values"].get(k)
                                for k in sorted(q)},
                             "order_p": rch["order_p"],
                             "q_extrap": rch["q_extrap"],
                             "change_last": rch["change_last"]})
                print(f"[corner-ana] convergence n={n} Re={Re:g} {d}: "
                      f"p={rch['order_p']} "
                      f"change_last={rch['change_last']}", flush=True)

    with (OUT_DIR / "corner_conv.csv").open("w", newline="",
                                            encoding="utf-8") as f:
        writ = csv.writer(f)
        keys = sorted({k for c in conv for k in c})
        writ.writerow(keys)
        for c in conv:
            writ.writerow([c.get(k) for k in keys])

    # ---------- md
    L = ["# Etude locale des coins — couches limites & corner eddy (chantier D)",
         "",
         "Reprise de l'algorithme canonique (campagne B) + streamfunction ",
         "canonique. Bande de coin = rayon rho autour des 4 coins de la boite ",
         "englobante (le domaine n=8, carre arrondi, n'atteint pas les coins : ",
         "f_corner_pctXX = fraction de dissipation dans la bande (XX = % de ",
         "L_c). ",
         "psi_corner_max = force du tourbillon secondaire de coin ; ",
         "n_vortex_pX = extrema secondaires au seuil X %.", ""]
    L.append("| cas | N | D/A | f_c pct10 | f_c pct20 | f_bl | f_br | "
             "n_v1 | psi_eddy |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for r in sorted(rows, key=lambda r: (r["n"], r["Re"], r["N"])):
        L.append(f"| {r['case_id']} | {r['N']} | {r['D_A']:.3e} | "
                 f"{r['f_corner_pct10']:.4f} | {r['f_corner_pct20']:.4f} | "
                 f"{r['fcorner_bl']:.4f} | {r['fcorner_br']:.4f} | "
                 f"{r['n_vortex_p1']} | {r['psi_corner_max']:.2e} |")
    L += ["", "## Convergence (Richardson) par (n, Re)", ""]
    L.append("| n | Re | diag | ordre p | q_extrap | change_last |")
    L.append("|---|---|---|---|---|---|")
    for c in conv:
        ext = "%.4e" % c["q_extrap"] if c["q_extrap"] is not None else "-"
        p_ = "%.2f" % c["order_p"] if c["order_p"] else "-"
        ch = "%.4f" % c["change_last"] if c["change_last"] is not None else "-"
        L.append(f"| {c['n']} | {c['Re']:g} | {c['diag']} | {p_} | {ext} | {ch} |")
    (OUT_DIR / "corner_bnd.md").write_text("\n".join(L) + "\n",
                                           encoding="utf-8")

    # ---------- json brut
    (OUT_DIR / "corner_bnd.json").write_text(
        json.dumps({"rows": rows, "convergence": conv}, indent=1,
                   allow_nan=True), encoding="utf-8")

    # ---------- figure : convergence en N de la fraction de coin et de l'eddy
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), constrained_layout=True)
    n8 = [r for r in rows if abs(r["n"] - 8.0) < 1e-9 and r["Re"] == 1000.0]
    if n8:
        byN = {r["N"]: r for r in n8}
        for d, ax in zip(("f_corner_pct20", "psi_corner_max"), axes):
            xs, ys = [], []
            for N_ in sorted(byN):
                v = byN[N_][d]
                if v == v and abs(v) > 0:  # pas nan, pas nul
                    xs.append(N_)
                    ys.append(abs(v))
            if xs:
                ax.loglog(xs, ys, "o-", label="n=8 Re=1000")
                ax.set_title(d)
                ax.set_xlabel("N")
                ax.grid(which="both", alpha=0.3)
    axes[0].legend(fontsize=8)
    fig.savefig(OUT_DIR / "corner_convergence.png", dpi=200)

    print(f"[corner-ana] ok -> {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())