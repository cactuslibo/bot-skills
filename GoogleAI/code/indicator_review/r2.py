import os,json,time,urllib.request
key=os.environ['GEMINI_API_KEY'];H={"Content-Type":"application/json","x-goog-api-key":key}
q2=json.load(open("qs.json"))[1]; prev=json.load(open("raw_1.json"))["id"]
body={"agent":"quant-indicator-auditor","input":q2,"environment":"remote","background":True,"previous_interaction_id":prev}
r=json.load(urllib.request.urlopen(urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/interactions",data=json.dumps(body).encode(),headers=H),timeout=300))
print("created",r["id"],r.get("status"),flush=True)
while r.get("status") in ("in_progress","queued","pending"):
    time.sleep(20)
    try: r=json.load(urllib.request.urlopen(urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/interactions/"+r["id"],headers=H),timeout=300))
    except Exception as e: print("poll err",e,flush=True); continue
    print(r.get("status"),flush=True)
json.dump(r,open("raw_2.json","w"),ensure_ascii=False); print("DONE",r.get("status"))
