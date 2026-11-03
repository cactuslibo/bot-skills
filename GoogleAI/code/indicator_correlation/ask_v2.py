import os,json,time,urllib.request,sys
key=os.environ['GEMINI_API_KEY'];H={"Content-Type":"application/json","x-goog-api-key":key};B="https://generativelanguage.googleapis.com/v1beta/interactions"
q=open(sys.argv[1]).read(); prev=sys.argv[3] if len(sys.argv)>3 else None
body={"agent":"quant-indicator-auditor","input":q,"environment":"remote","background":True}
if prev: body["previous_interaction_id"]=prev
r=json.load(urllib.request.urlopen(urllib.request.Request(B,data=json.dumps(body).encode(),headers=H),timeout=600))
print("created",r["id"],flush=True)
while r.get("status") in ("in_progress","queued","pending"):
    time.sleep(20)
    try: r=json.load(urllib.request.urlopen(urllib.request.Request(B+"/"+r["id"],headers=H),timeout=600))
    except Exception as e: print("poll err",e,flush=True)
json.dump(r,open(sys.argv[2],"w"),ensure_ascii=False); print("DONE",r.get("status"),flush=True)
