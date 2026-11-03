import os,json,time,urllib.request,urllib.error
key=os.environ['GEMINI_API_KEY'];H={"Content-Type":"application/json","x-goog-api-key":key}
B="https://generativelanguage.googleapis.com/v1beta/"
def call(url,body=None):
    req=urllib.request.Request(B+url,data=json.dumps(body).encode() if body else None,headers=H)
    try: return json.load(urllib.request.urlopen(req,timeout=600))
    except urllib.error.HTTPError as e: print("HTTP",e.code,e.read().decode()[:800],flush=True); raise
AID="ai-pharma-chain-reviewer"
try: a=call("agents/"+AID); print("exists",a.get("name"))
except urllib.error.HTTPError:
    body={"id":AID,"display_name":AID,"base_agent":"antigravity-preview-09-2026","agent_config":{"type":"antigravity","model":"gemini-3.8-flash"},
    "system_instruction":"You are a skeptical, independent reviewer of AI drug-discovery industry research. Cite real sources (URLs/DOIs) found via google_search/url_context for every external fact or number; never fabricate; mark anything unverifiable as UNVERIFIED.",
    "base_environment":"remote","tools":[{"type":"google_search"},{"type":"url_context"},{"type":"code_execution"}]}
    a=call("agents",body); print("created",json.dumps(a)[:500])
open("gai_agent_id.txt","w").write((a.get("name") or AID)+"\n")
num=lambda f:"".join(f"{i}\t{l}" for i,l in enumerate(open(f),1))
q1="""Act as a skeptical adversarial reviewer of the Chinese draft below (an AI drug-discovery industry chain framework + 4 bottleneck hypotheses), shown with line numbers; cite as draft_v1.md:Lnn. Today is 2026-11-01. Use google_search/url_context and give a real URL or DOI for every external fact/number; mark UNVERIFIED otherwise. Answer in English with sections:
(a) Structure: gaps or misplacements in upstream/midstream/downstream — where foundation-model companies, cloud/big-tech (Isomorphic/Google DeepMind, NVIDIA BioNeMo), lab automation, data licensors, CRO/CDMO belong; who actually captures profit (with evidence). Propose a corrected structure.
(b) For EACH of the 4 hypotheses (L7-L10): falsifiable as written? real bottleneck or symptom? evidence that would confirm/refute; key metric(s) to track with data source; a rewritten falsifiable version.
(c) Missing bottlenecks: target biology validity, translational/animal-model gap, talent, IP/patentability of AI-assisted inventions (USPTO guidance), compute cost, data-sharing incentives (federated efforts), others.
(d) Over-optimism risks.
(e) Concrete data requests for news.md, chain.md, market.md (items, sources, fields).

=====draft_v1.md=====
"""+num("draft_v1.md")
q2="""Second task (same review): audit market.md below (line numbers; cite market.md:Lnn). Spot-check numbers against PRIMARY sources (SEC filings, HKEX announcements, company press releases, exchange data) with URLs: market caps, YTD moves, Recursion cash and free cash flow, Insilico–Lilly deal terms, XtalPi–DoveTree deal terms, and DealForma 2025 figures ($29.7B headline vs ~$0.8B upfront). For each checked item give: Correct / Partly / Wrong / UNVERIFIED, correct value, source URL, date. Also flag currency mixing (USD/HKD/RMB), date-basis inconsistencies, and claims resting only on secondary sources. End with a prioritized fix list.

=====market.md=====
"""+num("market.md")
prev=None
for i,(q,out) in enumerate([(q1,"review_googleai_r1_raw.md"),(q2,"review_googleai_market_r1_raw.md")],1):
    body={"agent":AID,"input":q,"environment":"remote","background":True}
    if prev: body["previous_interaction_id"]=prev
    try: r=call("interactions",body)
    except urllib.error.HTTPError:
        body["environment"]="6898496e634eb79f120e9ae782c9c667"; r=call("interactions",body)
    print("iid",i,r["id"],flush=True)
    while r.get("status") in ("in_progress","queued","pending"):
        time.sleep(20)
        try: r=call("interactions/"+r["id"])
        except Exception as e: print("poll err",e,flush=True)
    print(i,r.get("status"),flush=True); prev=r["id"]
    json.dump(r,open(f"gai_raw_{i}.json","w"),ensure_ascii=False)
    mo=[s for s in r.get("steps",[]) if s.get("type")=="model_output"]
    open(out,"w").write("\n".join(c.get("text","") for c in (mo[-1]["content"] if mo else [])))
