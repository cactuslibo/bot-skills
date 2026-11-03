import json,os,sys,re
D='/workspace/agent-tools/'; L='qlog.json'; R='repos.json'
log=json.load(open(L)) if os.path.exists(L) else []
db=json.load(open(R)) if os.path.exists(R) else {}
rnd=sys.argv[1]; kind=sys.argv[2]; a=sys.argv[3:]
for k,q in zip(a[::2],a[1::2]):
    f=[x for x in os.listdir(D) if x.startswith(k)][0]; t=open(D+f).read()
    i=t.find('{"total_count') if '{"total_count' in t else t.find('{')
    d=json.JSONDecoder().raw_decode(t[i:])[0]
    it=d.get('items',[]); new=0; seen=set()
    for x in it:
        r=x['repository']['full_name'] if kind=='code' else x['full_name']
        if r in seen: continue
        seen.add(r)
        if r not in db: db[r]={'q':[],'paths':[],'round':rnd}; new+=1
        db[r]['q'].append(q)
        if kind=='code': db[r]['paths'].append(x['path'])
        else: db[r].update(stars=x['stargazers_count'],pushed=x['pushed_at'][:10],desc=(x.get('description') or '')[:150])
    log.append(dict(round=rnd,channel='github_'+kind,query=q,total=d.get('total_count'),returned=len(it),unique=len(seen),new=new))
    print('##',q,d.get('total_count'),len(seen),'new',new)
json.dump(log,open(L,'w'),indent=0,ensure_ascii=False); json.dump(db,open(R,'w'),indent=0,ensure_ascii=False)
print('total repos',len(db))
