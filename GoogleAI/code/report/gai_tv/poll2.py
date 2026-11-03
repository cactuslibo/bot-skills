import os,json,time,urllib.request
ID="v1_ChdEQ0htYXBDcE9kbkF4ZElQdHR1aHNRcxIXVHlqbWFwbldMdkdmb19VUHA3elNvQVE"
H={'x-goog-api-key':os.environ['GEMINI_API_KEY']}
while True:
    try: r=json.load(urllib.request.urlopen(urllib.request.Request('https://generativelanguage.googleapis.com/v1beta/interactions/'+ID,headers=H),timeout=600))
    except Exception as e: print("err",e,flush=True); time.sleep(20); continue
    if r.get("status") not in ("in_progress","queued","pending"): break
    time.sleep(20)
print(r.get("status"),flush=True)
json.dump(r,open("raw_2.json","w"),ensure_ascii=False)
txt="\n".join(s.get("text","") or "".join(c.get("text","") for c in s.get("content",[]) if isinstance(c,dict)) for s in r.get("steps",[]) if s.get("type")=="model_output")
open("r2.txt","w").write(txt)
q=open("run.py").read().split('q2="')[1].split('"\n')[0]
open("../tv_short_review_transcript.md","a").write(f"## 第 2 轮\n**问：** {q}\n\n**interaction id:** {ID} status={r.get('status')}\n\n**答：**\n\n{txt}\n\n---\n\n")
