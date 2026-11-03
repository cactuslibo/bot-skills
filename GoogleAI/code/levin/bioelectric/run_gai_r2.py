import os,json,time,urllib.request,urllib.error,sys
key=os.environ['GEMINI_API_KEY'];H={"Content-Type":"application/json","x-goog-api-key":key}
B="https://generativelanguage.googleapis.com/v1beta/"
def call(url,body=None):
    req=urllib.request.Request(B+url,data=json.dumps(body).encode() if body else None,headers=H)
    try: return json.load(urllib.request.urlopen(req,timeout=600))
    except urllib.error.HTTPError as e: print("HTTP",e.code,e.read().decode()[:800],flush=True); raise
AID="bioelectric-levin-reviewer"
try: a=call("agents/"+AID); print("exists",flush=True)
except urllib.error.HTTPError:
    a=call("agents",{"id":AID,"display_name":AID,"base_agent":"antigravity-preview-09-2026","agent_config":{"type":"antigravity","model":"gemini-3.8-flash"},
    "system_instruction":"You are a skeptical, independent reviewer of bioelectricity / developmental biology literature reviews (Levin lab direction). Use ONLY English-language sources. Verify every citation (authors, year, journal, DOI) against Crossref/PubMed/publisher pages via google_search/url_context; never fabricate references; mark anything unverifiable as UNVERIFIED.",
    "base_environment":"remote","tools":[{"type":"google_search"},{"type":"url_context"},{"type":"code_execution"}]}); print("created",json.dumps(a)[:300],flush=True)
open("gai_agent_id.txt","w").write((a.get("name") or AID).split("/")[-1]+"\n")
AID=open("gai_agent_id.txt").read().strip()
num=lambda f:"".join(f"L{i}: {l}" for i,l in enumerate(open(f),1))
def run(tag,q,prev=None):
    body={"agent":AID,"input":q,"environment":"6898496e634eb79f120e9ae782c9c667","background":True}
    if prev: body["previous_interaction_id"]=prev
    i=call("interactions",body)["id"]; print(tag,"iid",i,flush=True); open("gai_iids.txt","a").write(f"{tag}2 {i}\n")
    while True:
        time.sleep(20)
        try: d=call("interactions/"+i)
        except Exception as e: print("poll err",e,flush=True); continue
        if d.get("status") not in("in_progress","queued","pending"): break
    print(tag,"status",d.get("status"),flush=True)
    json.dump(d,open(f"gai_raw_{tag}2.json","w"),ensure_ascii=False,indent=1)
    t=[s for s in d.get("steps",[]) if s.get("type")=="model_output"]
    open(f"branch{tag}_googleai_review_r2_raw.md","w").write("\n".join(c.get("text","") for c in t[-1]["content"]) if t else json.dumps(d)[:3000])
    return i
prevB=[l.split()[1] for l in open("gai_iids.txt") if l.startswith("B ")][0]
ask="""第 2 轮复核（全程中文，只用英文来源）。上一轮意见及我方核查后的最终版见下方 *_googleai_review.md（以它为准，其中已更正你上一轮的若干错误：Yam14 CSV 并未错位、Putney 2002 正确为 Annu Rev Pharmacol Toxicol 10.1146/annurev.pharmtox.42.092001.143801、Okamura PMID 19074969、Sem22 正确 DOI 10.1038/s41467-022-34363-w 等）。
请核对：1. 上轮必须修改/建议修改/建议补充是否逐条落实（引用 v2 行号 Lnn）；2. 修改是否引入新错误或前后不一致（含分级、篇数、新增章节）；3. 用 Crossref（api.crossref.org/works/DOI）抽查新增文献 DOI 的作者/年份/期刊/题名。
输出：「必须修改」「细节修改」分列；若无必须修改，明确写“同意”。不得编造，查不到标 UNVERIFIED。"""
ia=run("A",ask+"\n\n=====branchA_googleai_review.md=====\n"+open("branchA_googleai_review.md").read()+"\n=====changelog_v2.md=====\n"+open("changelog_v2.md").read()+"\n=====branchA_v2.md=====\n"+num("branchA_v2.md"),prevB)
run("B",ask+"\n\n=====branchB_googleai_review.md=====\n"+open("branchB_googleai_review.md").read()+"\n=====branchB_v2.md=====\n"+num("branchB_v2.md")+"\n=====branchB_papers.csv=====\n"+open("branchB_papers.csv").read()+"\n=====branchB_findings.md=====\n"+open("branchB_findings.md").read(),ia)
