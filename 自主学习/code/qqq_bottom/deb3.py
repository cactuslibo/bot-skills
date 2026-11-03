import json,sys
sys.argv=['x','none'];exec(open('g.py').read().split("m=sys.argv[1]")[0])
r1=open('debate_round1_gemini.md').read().split('## Response')[1]
P=f"""Debate round 3. You are the critical quant reviewer. In round 1 you wrote this critique and 5 candidates:
{r1}

The TradingView bot backtested your candidates and replied (tv_round2.md):
{open('tv_round2.md').read()}

Gate results (gates_table.md):
{open('tv_bt/gates_table.md').read()}

Key rebuttals to you: all 5 of your candidates failed your own gates (C1 Sharpe 0.40, bear branch only 6 triggers in 27y; C2 0.28; C3 17 trades, OOS 0.30; C4 OOS -0.03; C5 MDD -52%, 2022 Sharpe -2.09). Factual corrections: VIX3M starts 2007-12-05 (not 2015); Nasdaq ADVN/DECL full daily only from 2004; your WVF formula omitted the 0.85 x 50-day-high condition. P2 true out-of-sample 2008-2015 Sharpe 0.93 (0.77 with 5bp costs), so your 'P2 OOS luck' claim is rejected. Hard stops hurt (P1 Sharpe 0.84 -> 0.63 with -5% stop). Best so far: P2 overlay (100% QQQ when close>SMA200, +50% when P2 signal active): 7/15 gates, DSR 0.98, Sharpe 0.85, OOS 1.00, MDD -25% since 2008 vs buy&hold -49%, but 2022 Sharpe -0.77.

Goal: CONVERGE. Please:
1. Respond to each rebuttal/correction point by point: explicitly ACCEPT or CONTEST (with reasoning) each.
2. Propose AT MOST 3 refinements, focused mainly on fixing the P2 overlay's 2022 weakness (e.g. faster regime filter than SMA200 such as SMA50/SMA100 or dual-MA/slope, a VIX term-structure regime switch, a breadth filter using NDFI or ADVN/DECL from 2004). Each must be fully specified and codable on daily bars (signal at close, fill next open): exact base-exposure rule, exact add-on rule, exact exits, params, leverage financing assumption, plus a small parameter-neighborhood grid and which gates it must pass. Avoid hard stops unless justified given the evidence above. Keep the parameter count small to limit multiple testing.
3. State the SINGLE final combination you would recommend if none of the refinements passes, and why.
4. Revise your gates if any were unrealistic, and say so explicitly.
Be concise, numbered, specific."""
for m,t in [('gemini-3.8-flash',3),('gemini-3-flash-preview',3)]:
    r=call(m,P,False,t)
    if r: break
open('debate_round3_gemini.md','w').write(f"# Debate round 3 — Gemini\nModel: {m}\n\n## Prompt\n{P}\n\n## Response\n{r}\n"); print('OK',m); print(r)
