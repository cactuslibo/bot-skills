import json,importlib,numpy as np
from r5 import full_report
for modn in ['r8','r9']:
    mod=importlib.import_module(modn); m=mod.M('QQQ'); d=json.load(open(f'{modn}_results.json')); mx=0; bad=0; trd=0
    for r in d['rows']:
        lo,hi=mod.TRAIN[r['fam']]
        with np.errstate(invalid='ignore'): w=mod.build(m,r['fam'],r['p'])
        s=full_report(m,*w,lo,hi); tr=mod.triggers(m,r['fam'],lo,hi)
        diff=max(abs(s[k]-r['train'][k]) for k in r['train']); mx=max(mx,diff); bad+=diff>1e-9; trd+=tr!=r['trig']
    print(modn,len(d['rows']),'max diff',mx,'不一致',bad,'触发数不一致',trd)
