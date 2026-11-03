import yfinance as yf, json
out={}
for t in ["TEM","GH","CAI","NEO","NTRA","^TNX"]:
    tk=yf.Ticker(t); i=tk.info
    h=tk.history(period="5d")
    keys=["currentPrice","marketCap","enterpriseValue","totalRevenue","grossMargins","revenueGrowth","totalDebt","totalCash","sharesOutstanding","impliedSharesOutstanding","beta","ebitdaMargins","operatingMargins","freeCashflow","priceToSalesTrailing12Months","enterpriseToRevenue","regularMarketPreviousClose"]
    d={k:i.get(k) for k in keys}
    d["last_close"]=(str(h.index[-1].date()), float(h.Close.iloc[-1])) if len(h) else None
    try:
        ra=tk.revenue_estimate; d["rev_est"]=ra.to_dict() if ra is not None else None
    except Exception as e: d["rev_est"]=str(e)
    out[t]=d
print(json.dumps(out,indent=1,default=str))
