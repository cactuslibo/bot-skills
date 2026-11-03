import os,json,time,urllib.request,sys
key=os.environ['GEMINI_API_KEY'];H={"Content-Type":"application/json","x-goog-api-key":key};B="https://generativelanguage.googleapis.com/v1beta/interactions"
qs=json.load(open("qs_corr.json")); prev=json.load(open("/workspace/indicator_review/raw_2.json"))["id"]
for i,q in enumerate(qs,1):
    body={"agent":"quant-indicator-auditor","input":q,"environment":"remote","background":True}
    if prev: body["previous_interaction_id"]=prev
    try: r=json.load(urllib.request.urlopen(urllib.request.Request(B,data=json.dumps(body).encode(),headers=H),timeout=300))
    except urllib.error.HTTPError as e:
        m=e.read().decode();print("ERR",i,e.code,m[:800],flush=True)
        if i==1 and prev: prev=None; body.pop("previous_interaction_id"); r=json.load(urllib.request.urlopen(urllib.request.Request(B,data=json.dumps(body).encode(),headers=H),timeout=300))
        else: sys.exit(1)
    print("created",i,r["id"],flush=True)
    while r.get("status") in ("in_progress","queued","pending"):
        time.sleep(20)
        try: r=json.load(urllib.request.urlopen(urllib.request.Request(B+"/"+r["id"],headers=H),timeout=300))
        except Exception as e: print("poll err",e,flush=True)
    json.dump(r,open(f"raw_corr_{i}.json","w"),ensure_ascii=False); prev=r["id"]; print("DONE",i,r.get("status"),flush=True)
