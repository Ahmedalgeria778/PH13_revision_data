import math
import mpmath as mp
import numpy as np
from scipy.integrate import quad

mp.mp.dps = 50


def q_param(n, maxdegree=None):
    nn = mp.mpf(n)
    p = 2 / nn
    def f(th):
        c, s = mp.cos(th), mp.sin(th)
        return p * mp.sqrt(c ** (2*p-2) * s**2 + s ** (2*p-2) * c**2)
    kw = {"maxdegree": maxdegree} if maxdegree else {}
    return mp.quad(f, [mp.mpf(0), mp.pi/4, mp.pi/2], **kw)


def q_cart(n):
    nn = mp.mpf(n)
    def f(u):
        if u == 0:
            return nn ** (1/nn)
        un = u ** nn
        log_t = mp.log1p(-un)
        log_omtn = mp.log(-mp.expm1(nn * log_t))
        log_term = (2*nn-2)*log_t + (2/nn-2)*log_omtn
        base = mp.log(nn) + (nn-1)*mp.log(u)
        if log_term > 0:
            log_f = base + log_term/2
        else:
            log_f = base + mp.log1p(mp.exp(log_term))/2
        return mp.exp(log_f)
    return mp.quad(f, [mp.mpf(0), mp.mpf(1)])


def q_polyline(n, m=500001):
    y = np.linspace(0.0, 1.0, m)
    x = np.power(np.maximum(0.0, 1.0 - y**n), 1.0/n)
    seg = np.hypot(np.diff(x), np.diff(y))
    return float(seg.sum())


def q_scipy_cart(n):
    def f(u):
        if u == 0.0:
            return n ** (1.0/n)
        un = u ** n
        log_t = math.log1p(-un)
        z = n * log_t
        if z == 0.0:
            return n ** (1.0/n)
        log_omtn = math.log(-math.expm1(z))
        log_term = (2*n-2)*log_t + (2.0/n-2.0)*log_omtn
        base = math.log(n) + (n-1)*math.log(u)
        if log_term > 0.0:
            log_f = base + 0.5*log_term
        else:
            log_f = base + 0.5*math.log1p(math.exp(log_term))
        return math.exp(log_f)
    return quad(f, 0.0, 1.0, epsabs=1e-12, epsrel=1e-12, limit=500)


for n in (4.0, 8.0, 20.0, 100.0, 1000.0):
    print("n", n, flush=True)
    print("  polyline", q_polyline(n), flush=True)
    print("  cart mp ", mp.nstr(q_cart(n), 20), flush=True)
    print("  scipy   ", q_scipy_cart(n), flush=True)
    for md in (10, 14):
        try:
            print(f"  param mp maxdegree={md}", mp.nstr(q_param(n, md), 20), flush=True)
        except Exception as e:
            print(f"  param mp maxdegree={md} FAIL", type(e).__name__, str(e)[:80], flush=True)
