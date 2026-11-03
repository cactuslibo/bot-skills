import os,json,time,urllib.request,sys
H={"Content-Type":"application/json","x-goog-api-key":os.environ['GEMINI_API_KEY']}
B="https://generativelanguage.googleapis.com/v1beta/"
def call(url,body=None):
    return json.load(urllib.request.urlopen(urllib.request.Request(B+url,data=json.dumps(body).encode() if body else None,headers=H),timeout=600))
while not os.path.exists("fb_raw_3.json"): time.sleep(20)
prev=json.load(open("fb_raw_3.json"))["id"]
q="""第四轮：用户提供了官方美国文件 tv_us_universe.csv，与你已过滤的 616 条案例完全一致（symbol+flush_date 相同），并新增字段（见下 us_extra.csv，按 symbol+flush_date 与之前数据合并）：
- event_id/dup：同一事件聚类编号与重复标记（共 566 个事件，dup=True 50 条）。请据此做按事件去重的稳健性检验。
- crash_file：该文件自带的 crash 列只有 43 条为 True，看起来是更严格/更短窗口的定义（约等于新高后 63 交易日内跌到阈值），与任务给定定义（新高后 12 个月内 ETF/指数≥30%、个股≥40%，共 107 条）不同。主分析请继续使用任务定义（107/616），并把 crash_file、crash_strict、crash_loose 作为敏感性分析，说明结论是否随定义改变。dd63_pct=63日内回撤，days_to_trough=见底天数。
请在 code_execution 中计算，然后输出最终修订版结构化中文报告（仅美国，完整替代上轮报告，章节同上，另加“定义敏感性”一节）。数字必须来自代码，来源附URL，无法核实的标注“无法核实”。

=====us_extra.csv=====
"""+open("us_extra.csv").read()
r=call("interactions",{"agent":"fakebreak-crash-analyst","input":q,"environment":"remote","background":True,"previous_interaction_id":prev})
print("created 4",r["id"],flush=True)
while r.get("status") in ("in_progress","queued","pending"):
    time.sleep(30)
    try: r=call("interactions/"+r["id"])
    except Exception as e: print("poll err",e,flush=True)
print(4,r.get("status"),flush=True)
json.dump(r,open("fb_raw_4.json","w"),ensure_ascii=False)
txt=r.get("output_text") or "\n".join(o.get("text","") for o in r.get("outputs",[]) if isinstance(o,dict))
open("fb_r4.txt","w").write(txt)
open("/workspace/report/gai_independent_transcript.md","a").write(f"## 第 4 轮（官方美国文件 + 去重字段）\n**问：**\n\n{q}\n\n**interaction id:** {r['id']} status={r.get('status')}\n\n**答：**\n\n{txt}\n\n---\n\n")
