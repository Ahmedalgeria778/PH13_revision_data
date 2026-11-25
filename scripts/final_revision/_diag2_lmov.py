import mpmath as mp
mp.mp.dps = 40
n = 4.0
nn = mp.mpf(n)

def direct(u):
    un = u ** nn
    t = 1 - un
    omtn = -mp.expm1(nn * mp.log1p(-un))
    term = t ** (2*nn-2) * omtn ** (2/nn-2)
    return nn * u ** (nn-1) * mp.sqrt(1+term)

def logged(u):
    un = u ** nn
    log_t = mp.log1p(-un)
    log_omtn = mp.log(-mp.expm1(nn*log_t))
    log_term = (2*nn-2)*log_t + (2/nn-2)*log_omtn
    base = mp.log(nn)+(nn-1)*mp.log(u)
    if log_term > 0:
        log_f = base + log_term/2
    else:
        log_f = base + mp.log1p(mp.exp(log_term))/2
    return mp.exp(log_f)

for u in (mp.mpf('0.1'), mp.mpf('0.5'), mp.mpf('0.9')):
    print(u, mp.nstr(direct(u),20), mp.nstr(logged(u),20))
print('direct quad', mp.nstr(mp.quad(direct,[0,1]),20))
print('logged quad', mp.nstr(mp.quad(logged,[0,1]),20))
