from pathlib import Path
import re, collections
R = Path(r'C:\Users\user\Documents\Default Project\GIRVD (revised)\05_dataset')
dirs = ['data_all190','data_refine','data_conv256','data_conv256_lowRe','data_refine_seed',
        'data_convHR','data_convHR_extB','data_lid_projected']
for d in dirs:
    p = R / d
    fs = [f for f in p.glob('*.npz') if '_ckpt' not in f.name]
    c, rey, ns = collections.Counter(), collections.Counter(), collections.Counter()
    keysets = collections.Counter()
    import numpy as np
    for f in fs:
        m = re.match(r'se_n([0-9]+p[0-9]+)_Re([0-9]+)_N(\d+)', f.name)
        if m:
            ns[m.group(1)] += 1
            rey[int(m.group(2))] += 1
            c[int(m.group(3))] += 1
        else:
            print('UNPARSED', f.name)
    print(d, 'final_npz', len(fs), 'N', dict(c))
    print('  n:', sorted(ns.items()))
    print('  Re:', sorted(rey.items()))
