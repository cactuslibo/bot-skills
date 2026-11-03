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
    i=call("interactions",body)["id"]; print(tag,"iid",i,flush=True); open("gai_iids.txt","a").write(f"{tag} {i}\n")
    while True:
        time.sleep(20)
        try: d=call("interactions/"+i)
        except Exception as e: print("poll err",e,flush=True); continue
        if d.get("status") not in("in_progress","queued","pending"): break
    print(tag,"status",d.get("status"),flush=True)
    json.dump(d,open(f"gai_raw_{tag}1.json","w"),ensure_ascii=False,indent=1)
    t=[s for s in d.get("steps",[]) if s.get("type")=="model_output"]
    open(f"branch{tag}_googleai_review_raw.md","w").write("\n".join(c.get("text","") for c in t[-1]["content"]) if t else json.dumps(d)[:3000])
    return i
ask="""请只用英文来源，逐条核对三点：
1. 事实与引用是否准确：作者、年份、期刊、DOI；并判断引文（据摘要/全文）是否真正支持报告中的具体说法。逐条列出有问题的引用（引用行号 Lnn）。
2. 证据强度分级（A=直接实验/B=模型间接；1–3 相关性；各小节“强/中”）是否合理，指出应升降级的条目。
3. 是否遗漏关键文献或反方/批评观点（例如对“形态信息存于 Vmem”的质疑、Vmem 作为下游读出而非原因、通道药理学的非特异性、混杂因素）。补充文献必须给出可核验的 DOI 或 PubMed 链接；查不到标 UNVERIFIED，绝不编造。
输出：分「必须修改」「建议修改」「建议补充文献/反方观点」三部分，最后写总体结论：同意 / 修改后同意 / 不同意。"""
ia=run("A","分支 A 复核（全程中文）。主题：什么控制 Vmem 在组织和全身的分布与维持，形态信息存在哪里（Levin 方向）。\n"+ask+"\n\n=====branchA_draft.md=====\n"+num("branchA_draft.md")+"\n=====branchA_papers.csv=====\n"+open("branchA_papers.csv").read()+"\n=====branchA_findings.md=====\n"+open("branchA_findings.md").read()+"\n=====overview_findings.md=====\n"+open("overview_findings.md").read())
run("B","分支 B 复核（全程中文，标准同分支 A）。主题：Vmem 变化如何转化为细胞内生化反应，最终输出落在哪一层（基因转录、蛋白/翻译后修饰、表观遗传、翻译）。\n"+ask+"\n\n=====branchB_draft.md=====\n"+num("branchB_draft.md")+"\n=====branchB_papers.csv=====\n"+open("branchB_papers.csv").read()+"\n=====branchB_findings.md=====\n"+open("branchB_findings.md").read(),ia)
