from pathlib import Path
import re, collections
R = Path(r'C:\Users\user\Documents\Default Project\GIRVD (revised)\05_dataset')

def parse(f):
    m = re.match(r'se_n([0-9]+p[0-9]+)_Re([0-9]+)_N(\d+)', f.name)
    if not m:
        return None
    n = float(m.group(1).replace('p', '.'))
    return (n, int(m.group(2)), int(m.group(3)))

def load(d):
    out = {}
    for f in (R/d).glob('*.npz'):
        if '_ckpt' in f.name:
            continue
        k = parse(f)
        if k:
            out.setdefault(k, []).append(f)
    return out

d190 = load('data_all190')
dref = load('data_refine')
d256 = load('data_conv256')
dlow = load('data_conv256_lowRe')
dseed = load('data_refine_seed')
all256 = dict(d256)
for k, v in dlow.items():
    all256.setdefault(k, []).extend(v)
print('N256 raw files', sum(map(len, d256.values())) + sum(map(len, dlow.values())))
print('N256 distinct (n,Re,256)', len(all256))
print('duplicates', {k: [p.name for p in v] for k, v in all256.items() if len(v) > 1})
print('n256 extras not in d256', sorted(set(dlow)-set(d256)))
n128_union = dict(d190)
for src in (dref, dseed):
    for k, v in src.items():
        n128_union.setdefault(k, []).extend(v)
print('N128 union distinct', len(n128_union), '190+refine', len(set(d190)|set(dref)), '190+refine+seed', len(n128_union))
print('N256 keys not in N128 union (190+refine+seed):')
for k in sorted(set(all256)-set(n128_union)):
    print(' ', k, [p.name for p in all256[k]])
print('N256 keys not in 190 only:')
for k in sorted(set(all256)-set(d190)):
    print(' ', k)
print('count N256 in 190 only', len(set(all256)&set(d190)))
print('count N256 in 190+refine', len(set(all256)&(set(d190)|set(dref))))
print('count N256 in 190+refine+seed', len(set(all256)&set(n128_union)))
print('refine keys not in 190', sorted(set(dref)-set(d190)))
print('seed keys not in 190+refine', sorted(set(dseed)-set(d190)-set(dref)))
