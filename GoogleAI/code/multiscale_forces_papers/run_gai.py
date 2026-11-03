import os,json,time,urllib.request,urllib.error
key=os.environ['GEMINI_API_KEY'];H={"Content-Type":"application/json","x-goog-api-key":key}
B="https://generativelanguage.googleapis.com/v1beta/"
def call(url,body=None):
    req=urllib.request.Request(B+url,data=json.dumps(body).encode() if body else None,headers=H)
    try: return json.load(urllib.request.urlopen(req,timeout=600))
    except urllib.error.HTTPError as e: print("HTTP",e.code,e.read().decode()[:800],flush=True); raise
AID="multiscale-citation-checker"
try: a=call("agents/"+AID); print("exists",flush=True)
except urllib.error.HTTPError:
    body={"id":AID,"display_name":AID,"base_agent":"antigravity-preview-09-2026","agent_config":{"type":"antigravity","model":"gemini-3.8-flash"},
    "system_instruction":"You are a meticulous citation auditor for physics/applied-math literature. Verify every claim via google_search/url_context (Crossref, publisher pages, arXiv). Never fabricate DOIs or metadata; mark anything unverified as UNVERIFIED.",
    "base_environment":"remote","tools":[{"type":"google_search"},{"type":"url_context"},{"type":"code_execution"}]}
    a=call("agents",body); print("created",json.dumps(a)[:300],flush=True)
open("gai_agent_id.txt","w").write((a.get("name") or AID).split("/")[-1]+"\n")
AID=open("gai_agent_id.txt").read().strip()
rows=[l for l in open("list.md") if l.startswith("| ") and l.split("|")[1].strip().isdigit()]
q="""Audit the citations of this 160-paper list (topic: cross-scale interactions & coarse-grained modeling of forces: nuclear->chemical bonds->vdW/H-bond/electrostatics/Casimir/depletion->colloids/polymers/phase separation/active matter/tissues; math: EFT/RG, Mori-Zwanzig, DFT/DDFT, SCFT, PB/PNP, Cahn-Hilliard, homogenization). Columns: #|label|title|authors|year|venue|DOI|...
Tasks:
1. For each entry, flag fabricated papers, wrong authors/year/venue/DOI. Give evidence URL. Output a table: label | problem | evidence | suggested DOI/metadata. Only list problematic entries; then state count judged OK.
2. Priority: Den12 (DOI 10.1201/b15597-19 seems to be another chapter), Cah13 (original is J. Chem. Phys. 28, 258 (1958)), Sch22 (DOI truncated, maybe 10.1021/acspolymersau.2c00049), and DOI-less Lik13, Bra03, Bou23, Mcn19c, Sol15 - find correct DOIs.
3. List clearly missing core papers (e.g. Mori 1965, Zwanzig 1961, Noid 2008 MS-CG, Evans 1979 DFT, Asakura-Oosawa 1954, Lifshitz 1956, Derjaguin/Verwey-Overbeek DLVO, Weinberg EFT, Wilson RG, Marconi-Tarazona DDFT, Hyman 2014 LLPS, etc.) each with DOI.
4. Separate list of suggested DOI changes.
Answer in English. Never invent DOIs.

=====list rows=====
"""+"".join(rows)
body={"agent":AID,"input":q,"environment":"fe0e22b553a4741ee172e7ef3399c67b","background":True}
try: r=call("interactions",body)
except urllib.error.HTTPError:
    print("env fail, switching",flush=True); body["environment"]="6898496e634eb79f120e9ae782c9c667"; r=call("interactions",body)
print("iid",r["id"],body["environment"],len(rows),flush=True)
while r.get("status") in ("in_progress","queued","pending"):
    time.sleep(20)
    try: r=call("interactions/"+r["id"])
    except Exception as e: print("poll err",e,flush=True)
print("status",r.get("status"),flush=True)
json.dump(r,open("gai_raw_1.json","w"),ensure_ascii=False)
mo=[s for s in r.get("steps",[]) if s.get("type")=="model_output"]
open("googleai_check_raw.md","w").write("\n".join(c.get("text","") for c in (mo[-1]["content"] if mo else [])))
