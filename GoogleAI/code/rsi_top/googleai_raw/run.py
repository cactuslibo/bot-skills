import json,os,sys,time,requests
K=os.environ['GEMINI_API_KEY'];B='https://generativelanguage.googleapis.com/v1beta';H={'x-goog-api-key':K}
tag,promptfile=sys.argv[1],sys.argv[2];prev=sys.argv[3] if len(sys.argv)>3 else None
body={"agent":"rsi-top-reviewer","input":open(promptfile).read(),"background":True,"environment":os.environ.get("ENVID","remote")}
if prev: body["previous_interaction_id"]=prev
r=requests.post(f'{B}/interactions',headers=H,json=body,timeout=600);open(f'{tag}_create.json','w').write(r.text);print(r.status_code,r.text[:500])
iid=r.json()['id']
while True:
    time.sleep(20);g=requests.get(f'{B}/interactions/{iid}',headers=H,timeout=600);j=g.json()
    st=j.get('status');print(st,flush=True)
    if st not in('in_progress','queued','running','pending',None) or 'error' in j: break
open(f'{tag}_final.json','w').write(g.text)
out=[s for s in j.get('steps',[]) if s.get('type')=='model_output']
txt='\n'.join(c.get('text','') for s in out for c in (s.get('content') or [])) if out else ''
if not txt: txt=json.dumps(out,ensure_ascii=False)
open(f'{tag}_answer.md','w').write(txt);print('ID',iid);print(txt[:300])
