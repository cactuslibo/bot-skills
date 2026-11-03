import os,json,time,urllib.request,urllib.error,sys
key=os.environ['GEMINI_API_KEY'];H={"Content-Type":"application/json","x-goog-api-key":key}
B="https://generativelanguage.googleapis.com/v1beta/"
def call(url,body=None):
    req=urllib.request.Request(B+url,data=json.dumps(body).encode() if body else None,headers=H)
    return json.load(urllib.request.urlopen(req,timeout=600))
P='/workspace/pattern_fakebreak/'
rep=open('/workspace/report/report_v2.md').read()
s1=open(P+'scan_v2.py').read();s2=open(P+'v2_extra.py').read()
cases=open(P+'v2_cases.csv').read()
ctr=open(P+'v2_counter.csv').read()
q=f"""第三轮（二审）：报告已按你前两轮意见修改为 v2（末尾有修订对照表）。下面给出 v2 全文、两个脚本、正例 v2_cases.csv（82 条，全文）和反例 v2_counter.csv（316 条，全文）。基准样本由 scan_v2.py 内每 5 日抽样生成（10,638 点），价格原始数据无法上传。
v2 新结论：形态本身不是看跌信号——正例收复后 60 日内最大回撤≥10% 的占比 13.4%，全样本基准 26.5%。
请：
1) 逐条核查第一轮 P0 是否已解决：①统一价格口径（复权/点位）；②做市商 gamma 符号与动态；③Heisenberg 2021 的错误归因；④“顶部”定义中的前瞻偏差。每条给出：已解决/部分解决/未解决 + 理由。
2) 评估新统计的方法与基准：基准是否可比（正例以“接近新高”为条件而基准不是）、重叠窗口与独立性、样本量与显著性检验（脚本用 Mann-Whitney）、正例的筛选、幸存者偏差、26.5% 基准是否用相同品种与区间（品种构成权重是否一致）。可用 code_execution 对 CSV 计算。
3) 核查 v2 新增内容的事实错误。
4) 如报告中出现以下两条引用，确认已更正：Banyi 的 DOI 应以 .004 结尾；Gabaix-Koijen 应为 NBER w28967。
5) 明确结论：能否定稿；列出剩余必须修改项（按优先级）。

=====report_v2.md=====
{rep}

=====scan_v2.py=====
{s1}

=====v2_extra.py=====
{s2}

=====v2_cases.csv=====
{cases}

=====v2_counter.csv=====
{ctr}
"""
prev=sys.argv[1] if len(sys.argv)>1 else 'v1_ChcwUXZtYXR1d01QUE55dE1QeVp2MHlRVRIXaUFfbWFybmhKb3oxeXRNUDdfYlVtUVU'
body={"agent":"pattern-report-reviewer","input":q,"environment":"remote","background":True}
if prev!='none': body["previous_interaction_id"]=prev
else: body["input"]="（新会话。前两轮 P0 摘要如下）\n"+open('/workspace/report/p0sum.txt').read()+"\n\n"+q
try: r=call("interactions",body)
except urllib.error.HTTPError as e: print("ERR",e.code,e.read().decode()[:1500]);sys.exit(2)
print("created",r["id"],flush=True)
while r.get("status") in ("in_progress","queued","pending"):
    time.sleep(30)
    try: r=call("interactions/"+r["id"])
    except Exception as e: print("poll err",e,flush=True)
print(r.get("status"),flush=True)
json.dump(r,open("raw_3b.json","w"),ensure_ascii=False)
txt=r.get("output_text") or "\n".join(o.get("text","") for o in r.get("outputs",[]) if isinstance(o,dict))
open("r3b.txt","w").write(txt)
open("/workspace/report/googleai_agent_transcript.md","a").write(f"## 第 3b 轮（二审 v2，新会话）\n**问：** {q[:2500]}…(报告全文、脚本、CSV 略)\n\n**previous_interaction_id:** {prev}\n\n**interaction id:** {r['id']} status={r.get('status')}\n\n**答：**\n\n{txt}\n\n---\n\n")
