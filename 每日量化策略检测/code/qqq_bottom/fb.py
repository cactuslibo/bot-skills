import json,sys,csv
sys.argv=['x','none'];exec(open('g.py').read().split("m=sys.argv[1]")[0])
models=open('models.json').read(); res=open('backtest_results.csv').read(); oos=open('oos_split.csv').read()
P=f"""You previously proposed these 12 QQQ bottom-detection models (JSON):
{models}

They were backtested on QQQ daily 2016-01-22..2026-10-28 (signal at close, fill next open, no costs, 100% position when in trade, 0% cash return). Buy&hold: CAGR 20.3%, MDD -35.6%, Sharpe 0.93 (2016-2021 Sharpe 1.17, 2022-2026 Sharpe 0.66 MDD -35.2%).
Full-period results:
{res}
In-sample (2016-2021) vs out-of-sample (2022-2026) split:
{oos}

Satisfaction criteria: >=30 trades over full period; Sharpe >=0.8; MaxDD better than -15%; profit factor >=1.5; OOS Sharpe >=0.5 and not collapsing vs IS; behaves as a genuine bottom-buy signal.
Specific dissatisfactions:
- ALL models: Sharpe 0.11-0.60 vs buy&hold 0.93; exposure 0.4%-35% so CAGR 0.4-7% vs 20%. None meets Sharpe>=0.8.
- #1 RSI(2): best risk-adjusted (Sharpe 0.60, MDD -10%, 87 trades, 71% win, PF 2.3, OOS Sharpe 0.75 stable) but exposure only 16%, CAGR 4.6%.
- #2 VIX Stretch: 172 trades, total +92%, but Sharpe 0.51, MDD -17.6% (>15%), PF 1.48.
- #3 Williams VIX Fix: total +104%, but MDD -29.7%, Sharpe 0.48; OOS Sharpe drops 0.64 -> 0.29. Condition 'WVF>10' fires during prolonged declines (bought too early).
- #4 FTD: only 1 trade (entered 2016, never exited, essentially buy&hold); 'new cycle low' definition and exit too loose; needs explicit correction-depth requirement (e.g. drawdown from high) and a working exit.
- #5 VIX/VIX3M: ambiguous rule (had to be reinterpreted as ratio>1.0 in prior 5 days then cross below 0.95); MDD -39% worse than buy&hold; OOS Sharpe -0.45 (collapsed from 0.97); avg hold 29 days; exit 'RSI14>70 or ratio>1' lets losses run.
- #6 Zweig Breadth Thrust: only 1 trade in 10 years (Nasdaq advancers/decliners via ADVN.NQ/DECL.NQ; Nasdaq breadth rarely thrusts like NYSE); need Nasdaq-adapted thresholds.
- #7 IBS: PF 6.7, 82% win, MDD -12%, but only 27 trades and exposure 4.6%.
- #8 % NDX stocks above 50DMA (used INDEX:NDFI): 16 trades, MDD -32%, Sharpe 0.41.
- #9 Smash Day: Sharpe 0.30, 53% win, IS Sharpe -0.47 vs OOS 0.86 (unstable).
- #10 3-Day Low: 80% win but Sharpe 0.41, OOS Sharpe 0.27, 41 trades, exposure 7.5%.
- #11 ATR Expansion: only 1 trade (ATR at 20-day high AND close < SMA20-2.5sd AND up day is too strict).
- #12 VIX RSI(2): ambiguous 'crosses below 70' (reinterpreted as RSI(VIX,2)>90 in prior 5 days then cross below 70); Sharpe 0.39; OOS Sharpe -0.11 collapsed from 0.89.

Please revise the models: (a) make every rule fully unambiguous and codable on daily bars (signal at close, entry next open), with exact parameters and an explicit max-holding/stop exit; (b) loosen or rework the ones with ~1 trade (#4, #6, #11) so they produce >=20 trades over 10 years while staying genuine bottom signals; (c) improve weak/unstable ones (#3, #5, #8, #9, #10, #12) or explicitly recommend dropping them; (d) propose 2-4 'overlay on buy&hold' variants (e.g. base 100%/partial QQQ exposure with leverage or added exposure on bottom signals, or a regime filter that keeps long most of the time and only adds on bottoms) that can beat buy&hold risk-adjusted. Only use data: QQQ daily OHLCV, VIX, VIX3M, Nasdaq advancing/declining issues, NDFI (% Nasdaq-100 stocks above 50DMA).
Return ONLY a JSON array. Each element: id (e.g. "1v2", or "O1" for overlays), based_on (original model # or null), action ("revise"|"keep"|"drop"|"new"), name, logic, entry_rule, exit_rule, params (object), required_data (array), change_rationale (what changed and why, referencing the numbers above)."""
used=None
for m,t in [('gemini-3.8-flash',3),('gemini-3-flash-preview',3)]:
    r=call(m,P,True,t)
    if r: used=m;break
open('gemini_feedback_raw.md','w').write(f"# Gemini feedback round\nModel: {used}\n\n## Prompt\n{P}\n\n## Response\n{r}\n")
json.dump(json.loads(r),open('models_v2.json','w'),indent=2,ensure_ascii=False); print('OK',used)
