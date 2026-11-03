import os,json,time,urllib.request,urllib.error,sys
H={"Content-Type":"application/json","x-goog-api-key":os.environ['GEMINI_API_KEY']}
B="https://generativelanguage.googleapis.com/v1beta/"
def call(url,body=None):
    return json.load(urllib.request.urlopen(urllib.request.Request(B+url,data=json.dumps(body).encode() if body else None,headers=H),timeout=600))
D='/workspace/quant_myrsi_v3/'
def num(f):
    L=open(D+f).read().splitlines(); return f"\n===== FILE {f} ({len(L)} lines) =====\n"+"\n".join(f"{i+1:4d}\t{x}" for i,x in enumerate(L))
pre="""You are an independent, skeptical quant reviewer. Answer in ENGLISH. You cannot read local files; all materials are pasted below with line numbers (REVIEW_REQUEST.md already embeds report.md, VAL_LOG.md, PLAN.md, v3.py, run_v3.py, compare_v3.py, td_snapshot.py with numbering). Cite file:line or JSON field for every claim; never invent numbers or lines. 2025-2026 are real historical data, not "future". Use code_execution to recompute stats where possible (e.g. binomial p for LOYO 0.171 vs 0.157, CP bounds).
File mtimes (America/New_York, 2026-11-01): td_snapshot.py 02:08:07; v3.py, run_v3.py 02:08:45; compare_v3.py, PLAN.md 02:09:25.96; HASHES.txt 02:09:25.97; go.sh 02:09:25.98; main_results.json 02:17:52; compare.json/compare.log 02:17:53; run.log 02:17:53.7; report.md, VAL_LOG.md, REVIEW_REQUEST.md 02:23:37. Current sha256 of all 5 hashed files recomputed now: identical to HASHES.txt. compare.log content is just "[]"-like 3 bytes. Note: the 2nd 2024 look ('mechanical recompute' via td.ev, 02:22) was done by a script NOT among the hashed files.
Tasks:
1. Are claimed results consistent with artifacts: G1-G8 all fail; LOYO precision 0.171 vs base 0.157, binomial p=0.38; 2024 22 triggers 2 hits; SPA p=0.859; PBO 0.68; trial counts 38,916 / cum 399,216 (note report sec.2 says 360,300->399,216).
2. Were the three changes implemented correctly and leak-free: vol-target scaled de-risking (prior-day 20d realized vol), trend-weakening (prior-day SMA / slope, shift(1)), confirmation nb + price buffer (kc bars, buf<=2%). Check t+1 execution and daily-return approximation.
3. Was the parameter-neighborhood robustness check (G7: jitter P10>0 among stab top-40; 200-jitter report) done properly; interpretation.
4. Was the code hash really recorded before the run, does it match current code.
5. 2024 contamination (viewed twice, logged) - impact on G2/G3; confirm no evidence 2026 data was opened (inspect code date filters).
6. Is "do not deploy" right; what next step.
Output: verdict, must-fix items, suggestions, each with citations; list any discrepancies found.
"""
p=pre+"\n"+num('REVIEW_REQUEST.md')
for f in ['HASHES.txt','go.sh','run.log','compare.log','main_results.json','compare.json']: p+=num(f)
open('prompt1.txt','w').write(p); print(len(p),flush=True)
r=None
for env in [None,'6898496e634eb79f120e9ae782c9c667','fe0e22b553a4741ee172e7ef3399c67b']:
    body={"agent":"rsi-top-reviewer","input":p,"background":True}
    if env: body["environment"]=env
    try: r=call("interactions",body); print("env",env,"id",r["id"],flush=True); break
    except urllib.error.HTTPError as e: print("env",env,"ERR",e.code,e.read().decode()[:300],flush=True)
if not r: sys.exit(3)
open('iid','w').write(r['id'])
while r.get("status") in ("in_progress","queued","pending"):
    time.sleep(20)
    try: r=call("interactions/"+r["id"])
    except Exception as e: print("poll err",e,flush=True)
print(r.get("status"),flush=True)
json.dump(r,open('final.json','w'),ensure_ascii=False)
mo=[s for s in r.get("steps",[]) if s.get("type")=="model_output"]
open('answer_en.md','w').write("\n".join(c.get("text","") for c in (mo[-1]["content"] if mo else []) if isinstance(c,dict)))
