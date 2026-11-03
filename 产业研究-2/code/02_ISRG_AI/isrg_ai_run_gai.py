import os,json,time,urllib.request,urllib.error
key=os.environ["GEMINI_API_KEY"];H={"Content-Type":"application/json","x-goog-api-key":key}
B="https://generativelanguage.googleapis.com/v1beta/"
def call(url,body=None):
    req=urllib.request.Request(B+url,data=json.dumps(body).encode() if body else None,headers=H)
    try: return json.load(urllib.request.urlopen(req,timeout=600))
    except urllib.error.HTTPError as e: print("HTTP",e.code,e.read().decode()[:800],flush=True); raise
AID="isrg-surgical-robot-reviewer"
try: a=call("agents/"+AID); print("exists",flush=True)
except urllib.error.HTTPError:
    body={"id":AID,"display_name":AID,"base_agent":"antigravity-preview-09-2026","agent_config":{"type":"antigravity","model":"gemini-3.8-flash"},
    "system_instruction":"You are a skeptical, independent reviewer of surgical-robotics / medtech industry research. Cite real sources (URLs) found via google_search/url_context for every external fact or number; never fabricate; mark anything unverifiable as UNVERIFIED.",
    "base_environment":"remote","tools":[{"type":"google_search"},{"type":"url_context"},{"type":"code_execution"}]}
    a=call("agents",body); print("created",json.dumps(a)[:300],flush=True)
open("gai_agent_id.txt","w").write((a.get("name") or AID).split("/")[-1]+"\n")
AID=open("gai_agent_id.txt").read().strip()
num=lambda f:"".join(f"{i}\t{l}" for i,l in enumerate(open(f),1))
q="""Independent red-team review of a Chinese research report (pasted with line numbers; cite report_v1.md:Lnn). Today is 2026-11-02. Topic: does the AI boom benefit the surgical-robot value chain and Intuitive Surgical (ISRG)? Draft conclusions: AI is moderately positive for ISRG, mainly via moat and higher system utilization; direct AI revenue uplift <1-2 pp over next 3 years; NVIDIA is the most certain beneficiary in the chain; biggest risk is AI lowering challengers' software/data barriers. Answer in English; use google_search/url_context; give URLs; mark UNVERIFIED; never invent numbers.
Tasks:
1. Verify key facts/numbers (AGREE/DISAGREE + source): Case Insights ~US$40k per system per year; da Vinci 5 utilization ~11% higher than Xi; per-procedure consumables (I&A) revenue down 3-5%; dates of Ottava De Novo and Hugo 510(k); Q3'26 revenue US$3.05B. Also any other numbers in the report.
2. Logic holes.
3. Missing evidence, e.g. autonomous surgery literature (STAR 2022 Science Robotics, SRT-H 2025), and others.
4. Separate section: ISRG fell sharply after Q3 2026 earnings — why? Give the reported figures (revenue, procedure growth, system placements, margins, EPS vs consensus), guidance changes, management commentary and the market reaction (% move, date), with sources.
Output: overall verdict (AGREE / CONDITIONAL AGREE / DISAGREE), numbered MUST-FIX list with line refs and concrete edits, SUGGESTED list.

=====report_v1.md=====
"""+num("report_v1.md")
body={"agent":AID,"input":q,"environment":"6898496e634eb79f120e9ae782c9c667","background":True}
try: r=call("interactions",body)
except urllib.error.HTTPError as e:
    print("env1 fail",flush=True); body["environment"]="fe0e22b553a4741ee172e7ef3399c67b"; r=call("interactions",body)
print("iid",r["id"],body["environment"],flush=True)
while r.get("status") in ("in_progress","queued","pending"):
    time.sleep(20)
    try: r=call("interactions/"+r["id"])
    except Exception as e: print("poll err",e,flush=True)
print("status",r.get("status"),flush=True)
json.dump(r,open("gai_raw_1.json","w"),ensure_ascii=False)
mo=[s for s in r.get("steps",[]) if s.get("type")=="model_output"]
open("googleai_review_r1_raw.md","w").write("\n".join(c.get("text","") for c in (mo[-1]["content"] if mo else [])))
