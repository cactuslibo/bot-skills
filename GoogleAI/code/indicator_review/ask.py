import os,json,sys,urllib.request
qs=json.load(open("qs.json"));_=[
"第1轮：讲清 AlphaGo(2016) 的演进路径：SL 策略网络→REINFORCE 自我对弈 RL 策略网络→价值网络→MCTS（含 fast rollout 与 λ 混合）。给出每步损失/更新公式（SL 交叉熵梯度；REINFORCE Δρ 含基线；价值 MSE）及所有训练超参数（步长、minibatch、步数、数据量），并给出 MCTS 选择/扩展/评估/回传公式、u(s,a)、Q/N 更新、virtual loss n_vl、n_thr、c_puct、λ、β 的数值。每项注明论文章节，没给出的写论文未给出。",
"第2轮：AlphaGo Zero(2017)：损失 l=(z−v)²−πᵀlog p+c‖θ‖² 及 c 值；PUCT 公式；Q/N/W 更新；是否用 virtual loss；c_puct 数值；π∝N^{1/τ} 及 τ 调度；Dirichlet α、ε；每步模拟数；评估局数与 55% 门控；resign 阈值规则；学习率调度（Extended Data Table 3 的确切分段步数）；batch；replay 窗口；动量；checkpoint 频率；20/40 block 规模数字。逐项注明出处。",
"第3轮：AlphaZero（arXiv 1712.01815 与 2018 Science 及补充材料/伪代码）：与 AGZ 的区别（去门控持续更新、和棋、对称增强）；每步模拟数；Dirichlet α 各游戏取值；学习率及降点步数；batch；训练步数；c_puct 形式（c_base、c_init）；L2 系数；τ/温度采样规则；resign 设置；replay 窗口。逐项注明 arXiv 版或 Science 版出处，有出入请指出。",
"第4轮：理论解释——引用 AGZ 论文原话说明 MCTS 为何是策略改进算子、z 为何是策略评估，以及为何整体等价于近似策略迭代；补充 Grill et al. 2020 的形式化结果（π̄ 定义、λ_N 公式），并注明哪些是后人分析。最后给出自我对弈/优化/评估并行的完整训练循环伪代码。"]
key=os.environ['GEMINI_API_KEY']; prev=None; out=open("agent_transcript.md","w")
out.write("# quant-indicator-auditor 原始回答记录\n\n")
for i,q in enumerate(qs,1):
    body={"agent":"quant-indicator-auditor","input":q,"environment":"remote","background":True}
    if prev: body["previous_interaction_id"]=prev
    req=urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/interactions",data=json.dumps(body).encode(),headers={"Content-Type":"application/json","x-goog-api-key":key})
    try:
        r=json.load(urllib.request.urlopen(req,timeout=120))
        import time
        while r.get("status") in ("in_progress","queued","pending"):
            time.sleep(15)
            g=urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/interactions/"+r["id"],headers={"x-goog-api-key":key})
            r=json.load(urllib.request.urlopen(g,timeout=120)); print(i,r.get("status"),flush=True)
    except urllib.error.HTTPError as e:
        msg=e.read().decode(); out.write(f"## 轮 {i} 失败\nHTTP {e.code}: {msg}\n\n"); print("ERR",i,e.code,msg[:500]); out.flush(); continue
    except Exception as e:
        out.write(f"## 轮 {i} 失败\n{e!r}\n\n"); print("ERR",i,e); out.flush(); continue
    prev=r.get("id",prev)
    txt=r.get("output_text")
    if not txt:
        txt="\n".join(o.get("text","") for o in r.get("outputs",[]) if isinstance(o,dict))
    if not txt: txt="(无 output_text，原始 JSON)\n```json\n"+json.dumps(r,ensure_ascii=False)[:20000]+"\n```"
    out.write(f"## 第 {i} 轮\n**问：** {q}\n\n**interaction id:** {r.get('id')} status={r.get('status')}\n\n**答：**\n\n{txt}\n\n---\n\n"); out.flush()
    json.dump(r,open(f"raw_{i}.json","w"),ensure_ascii=False); print("OK",i,r.get("id"),r.get("status"),len(txt))
