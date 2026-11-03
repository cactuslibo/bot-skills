import os,json,urllib.request
B='/workspace/qqq_hourly_rl/'
def rd(f,base=B): return f"\n===== {f} =====\n"+"".join(f"{i+1:4d}| {l}" for i,l in enumerate(open(base+f)))
ctx="".join(rd(f) for f in ['FIX_R8_9.md','forward_track.py','test_forward.sh','winrun2.py','r8.py','r9.py','r5.py','r6.py','engine.py','dsr_recalc_r8_9.py'])
ctx+=rd('dsr_check.py','/workspace/audit/')+rd('ladder_old.py','/workspace/audit/')+rd('clean_check.py','/workspace/audit/')
ctx+="""
===== 审核者运行结果 =====
--verify（真实数据，日志使用副本）：跳过 2026-10-29（QQQ_1h 缺少收盘 K 线 15:30，当日最后一根 11:30）；跳过 2026-10-30（QQQ 没有该日数据，VIX/VIX3M 最后一根 13:30，ADV_DECL 最后一根 14:30，且在第一个不完整日之后）；校验 0 行，差异 0，退出码 0。
test_forward.sh：T1 21 行、T2 +14、T3 跳过、T4 跳过、T5 0 差异、T6 1 处差异且退出码 1、T7 重建 42 行且 0 差异、T8 半日写入、T9 半日 13:05 跳过。真实 forward_log.csv 的 md5 不变。
DSR 独立复算：H2 0.244（SR 0.486，SR0 0.751）；H3 0.019（0.881，2.374）；G1 0.346（1.014，1.298）。
ladder 新旧代码在 24 组参数下权重和区间完全一致；r8 的 105 个、r9 的 36 个候选重算训练段指标，与 json 的差异为 0。
winrun2 用全部不合格的临时模块测试：在 SystemExit 之前打印 ERROR，OOS_LOG.md 的 md5 不变，没有生成 results 文件。
"""
Q="""你是独立的量化审计员。请核实下面对第 8–9 轮问题所做的修复，逐项给出 确认/可疑/无问题 的判断，并附文件名和行号：
1) forward_track.py 是否按 NYSE 日历判断"最后一根是收盘 K 线"，写入前是否逐个数据源校验都已收盘，是否截掉不完整的交易日，是否存在前视、副作用或测试覆盖上的漏洞（例如 --verify 是否会写文件、日线 VIX 数据源是否经过校验和截断、测试是否真正隔离）；
2) DSR 是否改为用训练段收益、配同一训练段全部候选的 SR 方差，实现是否正确；
3) r8/r9 清理前后结果是否一致；
4) winrun2 在全部候选不合格时，是否在查看验证集之前就退出。
最后列出仍需整改的事项。用中文回答。"""
key=os.environ['GEMINI_API_KEY']; body=json.dumps({"contents":[{"parts":[{"text":Q+"\n\n"+ctx}]}],"generationConfig":{"temperature":0.2}}).encode()
for model in ['gemini-3.8-flash','gemini-3-flash-preview']:
    try:
        r=urllib.request.Request(f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',data=body,headers={'Content-Type':'application/json','x-goog-api-key':key})
        j=json.load(urllib.request.urlopen(r,timeout=600)); txt="".join(p.get('text','') for p in j['candidates'][0]['content']['parts'])
        open(B+'gemini_audit_fix_r8_9.md','w').write(f"# Gemini 原始回复（模型 {model}，2026-10-30 ET）\n\n"+txt); print('OK',model); break
    except urllib.error.HTTPError as e: print(model,e.code,e.read()[:300])
