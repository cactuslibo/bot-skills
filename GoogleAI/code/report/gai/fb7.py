import os,json,time,urllib.request,urllib.error,sys
H={"Content-Type":"application/json","x-goog-api-key":os.environ['GEMINI_API_KEY']}
B="https://generativelanguage.googleapis.com/v1beta/"
def call(url,body=None):
    return json.load(urllib.request.urlopen(urllib.request.Request(B+url,data=json.dumps(body).encode() if body else None,headers=H),timeout=600))
def text(r): return "\n".join(c.get("text","") for s in r.get("steps",[]) if s.get("type")=="model_output" for c in s.get("content",[]) if isinstance(c,dict))
cmp=open('/workspace/report/compare_tv_gai.md').read()
res=open('/workspace/report/cmp/results.txt').read() if os.path.exists('/workspace/report/cmp/results.txt') else ''
q="""第三方复核方（股市诸葛）用统一口径复算了你上一轮报告，并提出 5 个问题。请诚实、逐条用中文回答；证据不支持的结论必须明确撤回。你上一轮的结论见本会话历史。

请特别注意：
- 问题 1、2：下面附有对方复算的 OR 表和聚类稳健检验结果（cmp/results.txt 原文）。可在 code_execution 中用这些计数自行复核（例如用 2x2 计数重算 OR/CI/p），并说明你的结论还剩哪些。对 FDR 结论：逐个因子（平台宽度、跌破深度、收复到新高天数、新高量比）说明聚类+剔除 2019-02~2020-03 后是否存活。
- 问题 3：请用 google_search/url_context 逐条访问 FRED 或美联储官方页面核实，给出 序列ID、日期、数值、URL；无法核实的直接删除。提示（请自己核实，不要照抄）：FRED FEDFUNDS 月度序列 https://fred.stlouisfed.org/series/FEDFUNDS ；目标利率 DFEDTAR（至 2008-12-15）https://fred.stlouisfed.org/series/DFEDTAR 与目标区间上限 DFEDTARU https://fred.stlouisfed.org/series/DFEDTARU ；FOMC 声明 https://www.federalreserve.gov/newsevents/pressreleases/monetary20070918a.htm ；HY OAS 序列 BAMLH0A0HYM2 https://fred.stlouisfed.org/series/BAMLH0A0HYM2 （注意：FRED 上该序列历史始于 1996-12 左右，且目前 FRED 公开下载只提供近 3 年数据，2007/2008/2020 的数值可能无法从 FRED 直接核实）。
- 问题 4：如能给出可复现规则，请写明规则并用会话中 F 节 107 条崩盘清单在 code_execution 中计算比例；否则撤回。
- 问题 5：更正年份计数，确认 2025-26 案例为真实历史数据（今天是 2026-10-31）。
最后给出一份“撤回/保留/修正”清单。每条注明证据来源（你自己的代码结果、URL，或对方复算结果）。

=====对方 5 个问题=====
1. 你们的 OR=1.54，形态组从新高日起算，反例组从跌破日起算。锚点统一后 OR 在 0.43–0.92 之间，最低一档 p<0.01。是否撤回“多头陷阱比真跌破更危险”？
2. 按跌破月份聚类并剔除 2019-02 至 2020-03 后，新高量比 p≈0.03–0.1。你们的 FDR 结论在聚类后还剩多少？
3. FRED 月度 FEDFUNDS 在 1989 年最高为 9.85%，不是 9.81%。请为 9.81%、HY OAS 2.5%/10.8%/21.8%、“425bp”、“2007-09-18 降息 50bp”分别给出序列、日期、数值来源，或删除。
4. “80% 以上的崩盘聚集在宏观窗口”请给出可复现规则和代码，或撤回。
5. 更正年份计数（2003-06 应为 8，2007-08 应为 15）；声明 2025-26 案例为真实历史数据。

=====对方对比文档 compare_tv_gai.md=====
"""+cmp+"\n\n=====对方复算结果 results.txt=====\n"+res
prev=json.load(open('us_raw_1.json'))['id']
envs=sys.argv[1:]
for env in envs:
    body={"agent":"fakebreak-crash-analyst","input":q,"environment":env,"background":True,"previous_interaction_id":prev}
    try: r=call("interactions",body);print("created",r["id"],"env",env,flush=True);break
    except urllib.error.HTTPError as e: print("ERR",env,e.code,e.read().decode()[:300],flush=True)
else: sys.exit(2)
while r.get("status") in ("in_progress","queued","pending"):
    time.sleep(30)
    try: r=call("interactions/"+r["id"])
    except Exception as e: print("poll err",e,flush=True)
print("done",r.get("status"),flush=True)
json.dump(r,open("q5_raw.json","w"),ensure_ascii=False);t=text(r);open("q5_r.txt","w").write(t)
open("/workspace/report/gai_independent_transcript.md","a").write(f"\n## 第 3 轮：回答股市诸葛 5 问\n**问：**\n\n{q[:4000]}\n…(对比文档与 results.txt 全文略，见 compare_tv_gai.md、cmp/results.txt)\n\n**environment:** {env}\n\n**interaction id:** {r['id']} status={r.get('status')}\n\n**答：**\n\n{t}\n\n---\n\n")
