import json, re, pathlib
R = pathlib.Path('/workspace/qqq_hourly_rl'); rd = lambda f: (R/f).read_text()
def heads(f): return '\n'.join(f'- {m}' for m in re.findall(r'^###\s+(.+)$', rd(f), re.M))
u1 = ("【背景材料：H2 首审 review_by_googleai.md】\n注意：该文件未标注为 Gemini 原始回复（文件内写明复核脚本为我方 review_fix.py），"
      "来源未核实，此处作为背景材料提供，不作为你的历史回复。\n\n" + rd('review_by_googleai.md') +
      "\n\n【第 6–7 轮审核请求】（原始提示词未存档；以下问题清单据 gemini_audit_r6_7.md 回复的各节标题还原）\n"
      "请作为独立量化审计员审计第 6–7 轮（r5.py/r6.py/r7.py、结果 json、报表与统计显著性），逐项给出判断与文件:行号证据：\n" + heads('gemini_audit_r6_7.md'))
u2 = ("【我方对第 6–7 轮 Gemini 意见的核实（audit_r6_7_verification.md）】\n" + rd('audit_r6_7_verification.md') +
      "\n\n【据此所做的整改（AUDIT_FIX_R6_7.md）】\n" + rd('AUDIT_FIX_R6_7.md') +
      "\n\n【第 8–9 轮复审请求（REVIEW_REQUEST_R8.md 原文）】\n" + rd('REVIEW_REQUEST_R8.md'))
u3 = ("【我方对第 8–9 轮 Gemini 意见的核实（audit_r8_9_verification.md）】\n" + rd('audit_r8_9_verification.md') +
      "\n\n【整改确认请求（FIX_R8_9.md 原文）】\n" + rd('FIX_R8_9.md'))
u4 = "【我方对整改复核 Gemini 意见的核实（audit_fix_r8_9_verification.md）】\n" + rd('audit_fix_r8_9_verification.md')
U = lambda t: {"role":"user","parts":[{"text":t}]}; M = lambda f: {"role":"model","parts":[{"text":rd(f)}]}
h = [U(u1), M('gemini_audit_r6_7.md'), U(u2), M('gemini_audit_r8_9.md'), U(u3), M('gemini_audit_fix_r8_9.md'), U(u4)]
json.dump(h, open(R/'gemini_chat/history.json','w'), ensure_ascii=False, indent=1)
print(len(h), sum(len(p['text']) for c in h for p in c['parts']))
