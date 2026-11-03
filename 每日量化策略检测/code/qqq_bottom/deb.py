import json,sys
sys.argv=['x','none'];exec(open('g.py').read().split("m=sys.argv[1]")[0])
P=f"""Act as a CRITICAL senior quant reviewer in a debate with another research agent (the 'TradingView bot'). Context: we are building QQQ (Nasdaq-100 ETF) bottom-buy signals. Data: QQQ daily OHLCV 2016-2026 (and since 2000 for robustness), VIX, VIX3M, Nasdaq adv/decl, NDFI. Backtest: signal at close, fill next open, no costs, 100% position, 0% cash.

=== TradingView bot's proposals (tv_proposals.md) ===
{open('tv_proposals.md').read()}

=== Index of Taz's 70 TradingView indicator scripts (index.md) ===
{open('tv_indicators/index.md').read()}

=== Your own earlier v2 revised models (models_v2.json) ===
{open('models_v2.json').read()}

Tasks:
1. Critique P1 (RSI2<15 & close>SMA200 buy, RSI2>70 sell) and P2 (RSI2<15 & VIX/VIX3M<1 buy, close>SMA5 sell) rigorously: overfitting, multiple testing over 172 combos (estimate deflated Sharpe / haircut), regime dependence (2016-2026 bull market, 2000-2002/2008 behavior, SMA200 filter missing bear-market bottoms), exit design (RSI2>70 vs SMA5 vs time stop, no stop-loss), VIX/VIX3M as proxy for vix_roll_yield, exposure/opportunity cost vs buy&hold.
2. Say which v2 ideas and which specific TV indicators from the index could be combined with P1/P2, and why.
3. Propose AT MOST 5 concrete, fully specified combination candidates: exact entry, exit, parameters, position sizing, and for each the robustness tests to run (parameter-neighborhood sweeps with exact grids, transaction costs e.g. 2/5/10 bps, since-2000 data, walk-forward, deflated Sharpe, regime splits). Must be codable on daily bars.
4. State the pass/fail criteria you would accept.
Be direct and specific; number everything."""
for m,t in [('gemini-3.8-flash',3),('gemini-3-flash-preview',3)]:
    r=call(m,P,False,t)
    if r: break
open('debate_round1_gemini.md','w').write(f"# Debate round 1 — Gemini critique\nModel: {m}\n\n## Prompt\n{P}\n\n## Response\n{r}\n"); print('OK',m); print(r)
