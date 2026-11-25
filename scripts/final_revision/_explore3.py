from pathlib import Path
import re
R = Path(r'C:\Users\user\Documents\Default Project\GIRVD (revised)\05_dataset')

def pairs(d):
    out = set()
    for f in (R/d).glob('*.npz'):
        if '_ckpt' in f.name:
            continue
        m = re.match(r'se_n([0-9]+p[0-9]+)_Re([0-9]+)_N(\d+)', f.name)
        if m:
            out.add((float(m.group(1).replace('p', '.')), int(m.group(2))))
    return out

p190, pref, pseed = pairs('data_all190'), pairs('data_refine'), pairs('data_refine_seed')
p256 = pairs('data_conv256') | pairs('data_conv256_lowRe')
print('pairs190', len(p190), 'refine', len(pref), 'seed', len(pseed), '256', len(p256))
for name, base in [('190', p190), ('190+refine', p190|pref), ('190+refine+seed', p190|pref|pseed)]:
    print(name, 'matched with 256:', len(p256 & base), 'unmatched:', sorted(p256 - base))
