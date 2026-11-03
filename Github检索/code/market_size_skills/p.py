import json,os,sys,collections
Q=dict(a.split('=',1) for a in sys.argv[1:])
fs={f[:8]:f for f in os.listdir('/workspace/agent-tools')}
log=json.load(open('raw/log.json')) if os.path.exists('raw/log.json') else []
db=json.load(open('raw/db.json')) if os.path.exists('raw/db.json') else {}
for k,q in Q.items():
    t=open('/workspace/agent-tools/'+fs[k]).read(); s=t[t.find('{"total_count'):]
    d=json.JSONDecoder().raw_decode(s)[0]; it=d.get('items',[])
    new=0
    for i in it:
        r=i['repository'] if 'repository' in i else i
        n=r['full_name']
        if n not in db: db[n]={"q":[],"paths":[],"stars":r.get('stargazers_count'),"desc":(r.get('description') or '')[:100]}; new+=1
        db[n]["q"].append(q)
        if 'path' in i and len(db[n]["paths"])<6: db[n]["paths"].append(i['path'])
    log.append({"query":q,"total":d.get('total_count'),"returned":len(it),"new_repos":new,"cum":len(db)})
    print(log[-1])
json.dump(log,open('raw/log.json','w'),indent=0);json.dump(db,open('raw/db.json','w'),indent=0)
