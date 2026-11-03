import sys,json,time
exec(open("run_gai.py").read().split("AID=")[0])
iid,out=sys.argv[1],sys.argv[2]
while True:
    try: r=call("interactions/"+iid)
    except Exception as e: print("err",e,flush=True); time.sleep(20); continue
    if r.get("status") not in ("in_progress","queued","pending"): break
    time.sleep(20)
print("status",r.get("status"),flush=True)
json.dump(r,open(out+".json","w"),ensure_ascii=False)
mo=[s for s in r.get("steps",[]) if s.get("type")=="model_output"]
open(out,"w").write("\n".join(c.get("text","") for c in (mo[-1]["content"] if mo else [])))
