import pickle, numpy as np, pandas as pd
OUT = "/workspace/wyckoff/full_bt"
R = pickle.load(open(f"{OUT}/raw_results.pkl", "rb"))
U = pd.read_csv("/workspace/wyckoff/universe.csv").drop_duplicates("ticker").set_index("ticker")
done, prep = [], []
for t, _, _, cur in R:
    if "V1_base" not in cur: continue
    c = cur["V1_base"]; o = c["out"]
    if not c["liq"] or c["last"] < pd.Timestamp("2026-10-20"): continue
    base = dict(代码=t, 名称=U.name.get(t), 行业=U.industry.get(t), 板块=U.sector.get(t), 市值_亿美元=round(U.market_cap.get(t) / 1e8, 1),
                最新日期=c["last"].date(), 最新收盘=round(c["close"], 2))
    v3 = cur.get("V3_pierce_clx", {}).get("out")
    last20 = o.iloc[-20:]; te = last20.index[last20.raw_test.to_numpy()]
    if len(te):
        T = te[-1]; sl = o.spring_low[T]; sp = o.index[(o.raw_spring.to_numpy()) & (o.index <= T)]
        after = c["low"][c["low"].index > T]
        if after.empty or after.min() >= sl:
            d = dict(base, Spring日期=sp[-1].date() if len(sp) else "窗口外", Spring低点_止损=round(sl, 2), Test日期=T.date(),
                     距止损pct=round((c["close"] / sl - 1) * 100, 2), 同时满足V3放量下破=bool(v3 is not None and v3.raw_test.get(T, False)))
            done.append(d)
    elif o.state.iloc[-1] == "SPRING":
        sp = o.index[o.raw_spring.to_numpy()][-1]; sl = o.spring_low.iloc[-1]
        prep.append(dict(base, Spring日期=sp.date(), Spring低点_止损=round(sl, 2), Test日期="等待中",
                         距止损pct=round((c["close"] / sl - 1) * 100, 2), 同时满足V3放量下破=bool(v3 is not None and v3.raw_spring.get(sp, False))))
D = pd.DataFrame(done).sort_values(["Test日期", "市值_亿美元"], ascending=[False, False])
P = pd.DataFrame(prep).sort_values(["Spring日期", "市值_亿美元"], ascending=[False, False])
D.to_csv(f"{OUT}/当前清单_已完成筑底.csv", index=False, encoding="utf-8-sig")
P.to_csv(f"{OUT}/当前清单_预备_等待Test.csv", index=False, encoding="utf-8-sig")
print(len(D), len(P)); print(D.head(15).to_string()); print(P.head(5).to_string())
