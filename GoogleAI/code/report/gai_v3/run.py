import os,json,time,urllib.request,urllib.error,sys
H={"Content-Type":"application/json","x-goog-api-key":os.environ['GEMINI_API_KEY']}
B="https://generativelanguage.googleapis.com/v1beta/"
def call(url,body=None):
    return json.load(urllib.request.urlopen(urllib.request.Request(B+url,data=json.dumps(body).encode() if body else None,headers=H),timeout=900))
def text(r): return "\n".join(c.get("text","") for s in r.get("steps",[]) if s.get("type")=="model_output" for c in s.get("content",[]) if isinstance(c,dict))
def num(p): return "\n".join(f"{i:4d}| {l}" for i,l in enumerate(open(p).read().splitlines(),1))
def run(q,prev,tag,env="remote"):
    body={"agent":"pattern-report-reviewer","input":q,"environment":env,"background":True}
    if prev: body["previous_interaction_id"]=prev
    for k in range(3):
        try: r=call("interactions",body);break
        except urllib.error.HTTPError as e:
            m=e.read().decode()[:1500];print("HTTP",e.code,m,flush=True)
            if e.code!=429 or k==2: sys.exit(2)
            time.sleep(60)
    print("created",tag,r["id"],flush=True)
    while r.get("status") in ("in_progress","queued","pending","running"):
        time.sleep(30)
        try: r=call("interactions/"+r["id"])
        except Exception as e: print("poll err",e,flush=True)
    print(tag,r.get("status"),flush=True)
    json.dump(r,open(f"raw_{tag}.json","w"),ensure_ascii=False)
    t=text(r);open(f"r_{tag}.txt","w").write(t);return r,t
