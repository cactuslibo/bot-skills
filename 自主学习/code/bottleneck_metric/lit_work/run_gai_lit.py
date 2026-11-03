import os,json,time,urllib.request,urllib.error
key=os.environ["GEMINI_API_KEY"];H={"Content-Type":"application/json","x-goog-api-key":key}
B="https://generativelanguage.googleapis.com/v1beta/"
def call(url,body=None):
    req=urllib.request.Request(B+url,data=json.dumps(body).encode() if body else None,headers=H)
    try: return json.load(urllib.request.urlopen(req,timeout=600))
    except urllib.error.HTTPError as e: print("HTTP",e.code,e.read().decode()[:800],flush=True); raise
AID=open("/workspace/ai_pharma/gai_agent_id.txt").read().strip()
q="""Independent CITATION VERIFICATION task (new topic, unrelated to earlier AI-pharma work): a literature list for the question "which firm financial metrics best identify supply-chain bottleneck/chokepoint firms". Today is 2026-11-01. Use google_search/url_context (doi.org, Crossref, publisher pages, SSRN/NBER). Answer in English. Never fabricate; mark UNVERIFIED anything you cannot check.
For EACH row below (format: key | title | authors | year | venue | DOI-or-link | grade | claimed finding in Chinese), report:
 - EXISTS? (Y/N/UNVERIFIED), and whether title/authors/year/venue/DOI are correct; give corrected values (e.g. the formal journal version, volume/pages, correct publication year) with URL.
 - CLAIM: does the claimed finding (Chinese text) match the paper's abstract/main result? (Correct / Partly / Wrong / UNVERIFIED) with a one-line reason. Flag any misattribution.
Then: (a) list important papers clearly MISSING for this question (e.g. profit persistence classics, upstreamness measures, gross profitability, smile-curve measurement, chokepoint/weaponized interdependence) with real DOIs; (b) an overall verdict and a numbered must-fix list.
Be concise: one line per row.

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
json.dump(r,open("gai_lit_raw.json","w"),ensure_ascii=False)
mo=[s for s in r.get("steps",[]) if s.get("type")=="model_output"]
open("gai_lit_review_raw.md","w").write("\n".join(c.get("text","") for c in (mo[-1]["content"] if mo else [])))
print("done",flush=True)
