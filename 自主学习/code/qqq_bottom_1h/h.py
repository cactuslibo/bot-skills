import json,sys
sys.argv=['x','none'];exec(open('g.py').read().split("m=sys.argv[1]")[0])
Q='/workspace/qqq_bottom/'
r3=open(Q+'debate_round3_gemini.md').read().split('## Response')[1]
P1=f"""You are a senior quant researcher. We just finished a multi-round research project on DAILY QQQ bottom-buy models. Lessons and final results:

=== TradingView bot round 2 (backtests of your candidates, data corrections) ===
{open(Q+'tv_round2.md').read()}

=== Your round-3 response ===
{r3}

=== TradingView bot round 3 (final verification and pick) ===
{open(Q+'tv_round3.md').read()}

Summary of lessons: final daily pick P2 (RSI(2)<15 & VIX/VIX3M<1 at close, buy next open, exit next open after close>SMA(5)); hard stops hurt mean reversion; VIX/VIX3M<1 acts as a stabilization filter (misses VIX-inverted panic bottoms); 441 cumulative trials so multiple-testing/DSR matters; results are cost-sensitive; agreed gates as revised above.

NEW PROJECT: design HOURLY-bar (1h K-line, regular session 09:30-16:00 ET, 7 bars/day with the first bar 09:30-10:30) QQQ bottom-buy models. Available data: QQQ 1h OHLCV, VIX 1h, VIX3M 1h (plus derivable daily bars). Propose 8-12 models. Include intraday-specific ideas: time-of-day/session effects, overnight gap, VWAP deviation (session VWAP from hourly bars), hourly RSI/IBS, multi-timeframe with daily regime (e.g. daily P2 state or daily SMA filters), VIX intraday spikes and term structure on hourly bars. For each model specify EXACTLY: name, logic, entry_rule (which bar's close generates signal, fill at next bar open or at close; behavior on last bar of day / overnight holding), exit_rule (bar-level, max holding bars, no hard stops unless justified), params (keep few to limit multiple testing), required_data, and a small parameter-neighborhood grid. Then define HOURLY-appropriate gates: costs (e.g. 1-2bp per side plus half-spread ~0.5-1bp; test 0/2/4bp), min trade count, IS/OOS split (state exact dates given hourly data typically only covers the last ~2-4 years on TradingView), DSR with cumulative trials, parameter-neighborhood stability, comparison to daily P2 and buy&hold. Be concrete and number everything."""
for m,t in [('gemini-3.8-flash',3),('gemini-3-flash-preview',3)]:
    r1=call(m,P1,False,t)
    if r1: break
P2="Convert the hourly models below into a JSON object with keys: models (array; each element keys: id, name, logic, entry_rule, exit_rule, params (object), param_grid (object), required_data (array of strings)) and gates (array of strings). Stay faithful to the text.\n\n"+r1
r2=call(m,P2,True,3)
open('gemini_models_raw.md','w').write(f"# Gemini hourly models\nModel: {m}\n\n## Prompt 1\n{P1}\n\n## Response 1\n{r1}\n\n## Prompt 2\n{P2[:200]}...\n\n## Response 2\n{r2}\n")
json.dump(json.loads(r2),open('models.json','w'),indent=2,ensure_ascii=False);print('OK',m);print(r1)
