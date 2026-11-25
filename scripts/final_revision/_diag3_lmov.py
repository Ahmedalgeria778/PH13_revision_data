import mpmath as mp
mp.mp.dps = 40
nn = mp.mpf(4)
u = mp.mpf('0.5')
un = u ** nn
t = 1 - un
log_t = mp.log1p(-un)
omtn = -mp.expm1(nn * log_t)
print('un', un, 't', t, 'log_t', log_t, 'omtn', omtn)
print('t^6', t ** (2*nn-2), 'omtn^-1.5', omtn ** (2/nn-2))
term = t ** (2*nn-2) * omtn ** (2/nn-2)
print('term', term, 'sqrt', mp.sqrt(1+term), 'f', nn*u**(nn-1)*mp.sqrt(1+term))
