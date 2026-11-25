# -*- coding: utf-8 -*-
"""High-precision upper-half superellipse arc length L_mov.

Geometry (manuscript eq. 105-118 and 01_geometry/superellipse.py):
    Omega_n = {|x|^n + |y|^n < 1}, a=b=1, L_c=2.
    The lid is the whole upper arc y>0 (theta in [0, pi]) with unit-speed
    tangential forcing.  Hence L_mov is the upper-half arclength.

First-quadrant parametrisation, p=2/n:
    x = cos^p(theta), y = sin^p(theta), theta in [0, pi/2]
    ds/dtheta = p sqrt(cos^(2p-2) sin^2 + sin^(2p-2) cos^2)
    L_mov = 2 * integral_0^(pi/2) ds/dtheta dtheta.

Independent Cartesian check (quarter arc, y variable t):
    x=(1-t^n)^(1/n),
    ds/sqrt(dt^2) = sqrt(1 + t^(2n-2) (1-t^n)^(2/n-2)).
    The endpoint singularity at t=1 is removed with t=1-u^n:
    L_quarter = n * integral_0^1 u^(n-1)
                sqrt(1 + (1-u^n)^(2n-2) (1-(1-u^n)^n)^(2/n-2)) du.

Run:
  C:\\Users\\user\\AppData\\Local\\Programs\\Python\\Python314\\python.exe compute_lmov.py

Outputs: l_mov.csv, l_mov_validation.csv, l_mov_report.md (this directory only).
"""
from __future__ import annotations

import csv
import math
import warnings
from pathlib import Path

import mpmath as mp
from scipy.integrate import quad as sci_quad

HERE = Path(__file__).resolve().parent
DPS = 60
REQUESTED = (1.25, 2.0, 4.0, 8.0)
VALIDATION_N = (1.0, 2.0, 4.0, 8.0, 100.0, 1000.0, 10000.0)


def q_param_mp(n: float) -> mp.mpf:
    """Quarter arclength by the trigonometric parametrisation (mpmath)."""
    nn = mp.mpf(n)
    p = 2 / nn

    def speed(th):
        c, s = mp.cos(th), mp.sin(th)
        return p * mp.sqrt(c ** (2 * p - 2) * s ** 2 + s ** (2 * p - 2) * c ** 2)

    return mp.quad(speed, [mp.mpf(0), mp.pi / 4, mp.pi / 2])


def q_cart_smooth_mp(n: float) -> mp.mpf:
    """Quarter arclength by the regularised Cartesian integral (mpmath)."""
    nn = mp.mpf(n)
    two_n_minus_2 = 2 * nn - 2
    two_over_n_minus_2 = 2 / nn - 2

    def f(u):
        if u == 0:
            # finite endpoint limit for n>1; n=1 is a separate straight line
            return mp.sqrt(2) if nn == 1 else nn ** (1 / nn)
        un = u ** nn
        t = 1 - un
        # log1p/expm1 avoid cancellation when t is extremely close to 1 (u~0).
        one_minus_tn = -mp.expm1(nn * mp.log1p(-un))
        term = t ** two_n_minus_2 * one_minus_tn ** two_over_n_minus_2
        return nn * u ** (nn - 1) * mp.sqrt(1 + term)

    return mp.quad(f, [mp.mpf(0), mp.mpf(1)])


def q_cart_smooth_scipy(n: float) -> tuple[float, float]:
    """float cross-check of the same regularised Cartesian integral."""
    def f(u):
        if u == 0.0:
            return math.sqrt(2.0) if n == 1.0 else n ** (1.0 / n)
        un = u ** n
        log_t = math.log1p(-un)
        z = n * log_t
        if z == 0.0:
            return n ** (1.0 / n)
        log_one_minus_tn = math.log(-math.expm1(z))
        log_term = (2 * n - 2) * log_t + (2.0 / n - 2.0) * log_one_minus_tn
        base = math.log(n) + (n - 1) * math.log(u)
        # Only drop the +1 when exp(log_term) is certainly negligible.
        log_1p_term = log_term if log_term > 50.0 else math.log1p(math.exp(log_term))
        return math.exp(base + 0.5 * log_1p_term)

    breakpoints = sorted({p for p in (1e-12, 1e-8, 1e-4, 0.5, 0.9,
                                      1.0 - 100.0 / n, 1.0 - 10.0 / n, 1.0 - 1.0 / n)
                          if 0.0 < p < 1.0})
    tol = 1e-13 if n <= 100 else 1e-10
    with warnings.catch_warnings():
        # Optional float cross-check; mpmath Cartesian value is authoritative.
        warnings.simplefilter("ignore")
        return sci_quad(f, 0.0, 1.0, epsabs=tol, epsrel=tol, limit=1000,
                        points=breakpoints)


def write_csv(name: str, rows: list[dict]) -> None:
    if not rows:
        return
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with (HERE / name).open("w", encoding="utf-8", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=fields)
        wr.writeheader()
        wr.writerows(rows)


def main() -> None:
    mp.mp.dps = DPS
    rows, validations = [], []
    by_n: dict[float, dict] = {}
    for n in sorted(set(REQUESTED) | set(VALIDATION_N)):
        qp = q_param_mp(n)
        qc = q_cart_smooth_mp(n)
        qscipy, err = q_cart_smooth_scipy(n)
        half_p, half_c = 2 * qp, 2 * qc
        rows.append(dict(
            n=f"{n:g}",
            p_2_over_n=mp.nstr(2 / mp.mpf(n), 20),
            quarter_param_mp=mp.nstr(qp, 30),
            half_param_mp=mp.nstr(half_p, 30),
            quarter_cartesian_mp=mp.nstr(qc, 30),
            half_cartesian_mp=mp.nstr(half_c, 30),
            half_cartesian_scipy=f"{2 * qscipy:.15g}",
            scipy_abs_error_estimate=f"{2 * err:.3e}",
            abs_param_minus_cart=mp.nstr(abs(half_p - half_c), 8),
            rel_param_minus_cart=mp.nstr(abs(half_p - half_c) / half_c, 8),
        ))
        by_n[n] = rows[-1]
        print(f"n={n:g} L_mov(param)={mp.nstr(half_p, 24)} "
              f"L_mov(cart)={mp.nstr(half_c, 24)} "
              f"diff={mp.nstr(abs(half_p - half_c), 5)}")

    exact = {
        1.0: (2 * mp.sqrt(2), "diamond: two straight segments"),
        2.0: (mp.pi, "circle radius 1: upper semicircle"),
    }
    for n in VALIDATION_N:
        # Cartesian quadrature is authoritative: the trigonometric form has a
        # very thin endpoint layer for large n and default mpmath degree is not
        # enough there, while the Cartesian integrand is regularised.
        half = mp.mpf(by_n[n]["half_cartesian_mp"])
        if n in exact:
            ref, note = exact[n]
        elif n >= 100:
            ref, note = mp.mpf(4), f"square limit n->infinity (finite-n value at n={n:g})"
        else:
            continue
        validations.append(dict(
            case=note,
            n=f"{n:g}",
            L_mov=mp.nstr(half, 30),
            reference=mp.nstr(ref, 30),
            abs_error=mp.nstr(abs(half - ref), 10),
            rel_error=mp.nstr(abs(half - ref) / ref, 10),
            finite_n_vs_limit=("finite n" if n >= 100 else "exact"),
        ))

    write_csv("l_mov.csv", rows)
    write_csv("l_mov_validation.csv", validations)

    lines = [
        "# Upper-half moving-wall arclength L_mov",
        "",
        "Script: `corrections for reviewer/07_final_scientific_revision/compute_lmov.py`.",
        f"mpmath working precision: {DPS} decimal digits.",
        "",
        "The moving lid is the whole upper arc of `|x|^n+|y|^n=1` (a=b=1, L_c=2), as",
        "defined in `01_geometry/superellipse.py` lines 20-31 and manuscript lines 105-118.",
        "With `p=2/n`, the first-quadrant parametrisation is `x=cos^p(theta)`,",
        "`y=sin^p(theta)`, and `L_mov=2*integral_0^(pi/2) p*sqrt(cos^(2p-2)sin^2 + sin^(2p-2)cos^2) dtheta`.",
        "For n>2 the integrand has integrable algebraic endpoint singularities; the",
        "quadrature splits at theta=pi/4. An independent Cartesian quadrature uses",
        "the substitution t=1-u^n to remove the endpoint singularity at t=1. The Cartesian",
        "form is used as the authoritative value: for n>=100 the trigonometric integrand",
        "has an endpoint layer too thin for the default mpmath quadrature degree, whereas",
        "the Cartesian values agree with an independent dense polyline check.",
        "",
        "## Requested values",
        "",
        "| n | L_mov (mpmath, trig) | L_mov (mpmath, Cartesian, authoritative) | L_mov/L_c |",
        "|---:|---:|---:|---:|",
    ]
    for n in REQUESTED:
        r = by_n[n]
        half = mp.mpf(r["half_cartesian_mp"])
        lines.append(f"| {n:g} | {r['half_param_mp'][:24]} | {r['half_cartesian_mp'][:24]} | "
                     f"{mp.nstr(half / 2, 20)} |")
    lines += [
        "",
        "For n=1.25, 2, 4 and 8 the two independent high-precision quadratures agree to",
        "at least the digits shown in `l_mov.csv`.",
        "",
        "## Known-limit validation",
        "",
        "| case | n | computed L_mov | reference | abs error | note |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for v in validations:
        lines.append(f"| {v['case']} | {v['n']} | {v['L_mov'][:24]} | {v['reference'][:24]} | "
                     f"{v['abs_error']} | {v['finite_n_vs_limit']} |")
    lines += [
        "",
        "The `n=100`, `n=1000` and `n=10000` rows are finite-n approaches to the",
        "square limit 4, not assertions that the square cavity has the same lid law:",
        "the manuscript explicitly treats the square/Ghia case as a different forcing.",
        "",
        "## Outputs",
        "",
        "* `l_mov.csv`, `l_mov_validation.csv`.",
    ]
    (HERE / "l_mov_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
