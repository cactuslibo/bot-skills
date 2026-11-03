import json,os,sys,time,requests
K=os.environ['GEMINI_API_KEY'];B='https://generativelanguage.googleapis.com/v1beta';H={'x-goog-api-key':K}
tag,iid=sys.argv[1],sys.argv[2]
while True:
    g=requests.get(f'{B}/interactions/{iid}',headers=H,timeout=600);j=g.json();st=j.get('status');print(st,flush=True)
    if st not in('in_progress','queued','running','pending') : break
    time.sleep(20)
open(f'{tag}_final.json','w').write(g.text)
txt='\n'.join(c.get('text','') for s in j.get('steps',[]) if s.get('type')=='model_output' for c in (s.get('content') or []))
open(f'{tag}_answer.md','w').write(txt);print(len(txt))
