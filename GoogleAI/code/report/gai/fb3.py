import os,json,time,urllib.request,sys
H={"Content-Type":"application/json","x-goog-api-key":os.environ['GEMINI_API_KEY']}
B="https://generativelanguage.googleapis.com/v1beta/"
def call(url,body=None):
    return json.load(urllib.request.urlopen(urllib.request.Request(B+url,data=json.dumps(body).encode() if body else None,headers=H),timeout=600))
while not os.path.exists("fb_raw_2.json"): time.sleep(20)
prev=json.load(open("fb_raw_2.json"))["id"]
q="""第三轮（范围变更，用户要求）：分析范围仅限美国上市标的——美国上市ETF/指数与美国大市值个股。排除A股及所有其他市场。
请在 code_execution 中将第一轮的 universe.csv 过滤为 market=='US'（616 条），重做所有统计（基准率、条件概率、显著性检验、聚类/去重稳健性、年份分布），删除所有A股相关内容（包括A股2015等）。美国反例组汇总如下（我方代码生成）。
然后输出最终结构化中文报告（仅美国）：摘要；数据与定义；基准率与条件概率表（精确 n/N）；形态特征；成交量；利率与美联储（附URL）；宏观（附URL）；年份聚集；稳健性与局限；结论（按证据强度分级）；来源列表。数字须来自代码，无法核实的标注“无法核实”。

"""+open("c_us_summary.txt").read()
r=call("interactions",{"agent":"fakebreak-crash-analyst","input":q,"environment":"remote","background":True,"previous_interaction_id":prev})
print("created 3",r["id"],flush=True)
while r.get("status") in ("in_progress","queued","pending"):
    time.sleep(30)
    try: r=call("interactions/"+r["id"])
    except Exception as e: print("poll err",e,flush=True)
print(3,r.get("status"),flush=True)
json.dump(r,open("fb_raw_3.json","w"),ensure_ascii=False)
txt=r.get("output_text") or "\n".join(o.get("text","") for o in r.get("outputs",[]) if isinstance(o,dict))
open("fb_r3.txt","w").write(txt)
open("/workspace/report/gai_independent_transcript.md","a").write(f"## 第 3 轮（范围变更：仅美国）\n**问：**\n\n{q}\n\n**interaction id:** {r['id']} status={r.get('status')}\n\n**答：**\n\n{txt}\n\n---\n\n")
