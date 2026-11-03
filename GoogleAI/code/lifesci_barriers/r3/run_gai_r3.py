import os,json,time,urllib.request,urllib.error
key=os.environ['GEMINI_API_KEY'];H={"Content-Type":"application/json","x-goog-api-key":key}
B="https://generativelanguage.googleapis.com/v1beta/"
def call(url,body=None):
    req=urllib.request.Request(B+url,data=json.dumps(body).encode() if body else None,headers=H)
    try: return json.load(urllib.request.urlopen(req,timeout=600))
    except urllib.error.HTTPError as e: print("HTTP",e.code,e.read().decode()[:800],flush=True); raise
AID=open("/workspace/ai_pharma/gai_agent_id.txt").read().strip()
q="""Independent CITATION VERIFICATION task (follow-up batch B88-B142 for a literature list on "entry barriers, switching costs, installed base, tying and CRO industry structure in life-science tools, DNA sequencing and contract research organizations"; earlier batch B01-B87 was already verified). Today is 2026-11-01. Use google_search/url_context (doi.org, Crossref, publisher pages, SSRN/NBER/RePEc). Answer in English. Never fabricate; mark UNVERIFIED anything you cannot check.
Below are NEWLY ADDED rows (format: key | title | authors | year | venue | DOI | grade | claimed finding in Chinese). Be concise: ONE line per row:
 key | EXISTS Y/N/UNVERIFIED | metadata OK / corrected values (formal journal version, year, DOI) | CLAIM Correct/Partly/Wrong/UNVERIFIED + short reason.
Prioritise checking: (1) any row whose DOI looks wrong or points to a different paper (misattribution); (2) rows marked 摘要不可得 (abstract unavailable) where the Chinese claim was inferred from the title; (3) working-paper rows that have a formal published version.
End with: overall verdict, count of rows with problems, and a numbered must-fix list.

=====TABLE=====
"""+open("table_for_gai.txt").read()
body={"agent":AID,"input":q,"environment":"6898496e634eb79f120e9ae782c9c667","background":True}
try: r=call("interactions",body)
except urllib.error.HTTPError:
    body["environment"]="fe0e22b553a4741ee172e7ef3399c67b"; r=call("interactions",body)
print("iid",r["id"],body["environment"],flush=True)
while r.get("status") in ("in_progress","queued","pending"):
    time.sleep(20)
    try: r=call("interactions/"+r["id"])
    except Exception as e: print("poll err",e,flush=True)
print("status",r.get("status"),flush=True)
json.dump(r,open("gai_new_raw.json","w"),ensure_ascii=False)
mo=[s for s in r.get("steps",[]) if s.get("type")=="model_output"]
open("gai_new_review_raw.md","w").write("\n".join(c.get("text","") for c in (mo[-1]["content"] if mo else [])))
print("done",flush=True)
