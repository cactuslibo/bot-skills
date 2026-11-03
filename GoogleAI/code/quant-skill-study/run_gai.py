import os,json,time,urllib.request,urllib.error
key=os.environ['GEMINI_API_KEY'];H={"Content-Type":"application/json","x-goog-api-key":key}
B="https://generativelanguage.googleapis.com/v1beta/"
def call(url,body=None):
    req=urllib.request.Request(B+url,data=json.dumps(body).encode() if body else None,headers=H)
    try: return json.load(urllib.request.urlopen(req,timeout=600))
    except urllib.error.HTTPError as e: print("HTTP",e.code,e.read().decode()[:800],flush=True); raise
AID="quant-indicator-reviewer"
try: a=call("agents/"+AID); print("exists",flush=True)
except urllib.error.HTTPError:
    body={"id":AID,"display_name":AID,"base_agent":"antigravity-preview-09-2026","agent_config":{"type":"antigravity","model":"gemini-3.8-flash"},
    "system_instruction":"You are a skeptical, independent reviewer of quantitative-finance indicators, factor research and backtest-statistics documentation. Cite real sources (URLs) found via google_search/url_context for every external fact or number; never fabricate; mark anything unverifiable as UNVERIFIED.",
    "base_environment":"remote","tools":[{"type":"google_search"},{"type":"url_context"},{"type":"code_execution"}]}
    a=call("agents",body); print("created",json.dumps(a)[:300],flush=True)
open("gai_agent_id.txt","w").write((a.get("name") or AID).split("/")[-1]+"\n")
AID=open("gai_agent_id.txt").read().strip()
num=lambda f:"".join(f"{i}\t{l}" for i,l in enumerate(open(f),1))
q="""第 1 轮复核（全程中文）。下面是一份量化指标解释底稿（附行号，引用 report2-indicators-draft.md:Lnn），分 10 类约 60 项，整理自 GitHub 上 26 个量化 skill；每项含定义、用法、阈值、原理、陷阱、出处。注意：底稿声明“阈值一律只取自源文件”，你无法访问源文件，所以对阈值请判断其是否合理/是否符合业界与文献惯例，而不是要求改成你认为的值。
请逐项审查：
1. 用法和原理是否正确、完整（公式请逐一核对，例如 DSR/PSR、ICIR t 值、Sortino、Kelly、Fitness、Black-Scholes d1/d2、半衰期、换手定义、成本模型等；可用 code_execution 验算）。
2. 阈值是否合理。
3. 是否漏掉重要陷阱。
另外两个待定点请明确表态：
A. Hurst 指数分界用 0.4/0.6 还是 0.5？请考虑小样本下 R/S 估计的偏差（Anis-Lloyd / Peters 修正、DFA 等），可用 code_execution 对随机游走模拟 n=100/250/1000 的 R/S Hurst 估计分布来说明。
B. 布林带、OBV、KDJ 要不要补常用参数？若补，给出标准参数与出处（原作者/权威来源）。
输出格式：按十类逐项，每项归入「同意」/「需修改」（写理由和建议替换文字）/「需补充」（写要补的内容）；最后汇总三类数量。给出公式、阈值时附出处 URL；查不到标 UNVERIFIED，不得编造。

=====report2-indicators-draft.md=====
"""+num("report2-indicators-draft.md")
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
