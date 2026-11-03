import json, html
D="2026-11-03"
old=json.load(open("state_2026-11-02_backup.json"))
oldmap={t["name"]:t for t in old["tracked_items"]}
NC="沿用 11-02 价格，今日未重新核实"
# name -> (price, store, note, verified, checked_today)
upd={
"Let's Play Chef 超市玩具组（Supermarket Playset）":(42.49,"Amazon（Amazon 自营）","Amazon Resale 二手 $39.09；Kohl's 清仓价 $24.99 但缺货；Target 价格未能读取",True),
"Cruise Ship 邮轮玩具组（含 Bluey、Bingo）":(56.99,"Amazon（Amazon 自营）","标价 $64.99；页面另有 $37.36 报价（疑为 Amazon Resale 二手，未核实）",True),
"Mega Bundle 家庭房屋 + BBQ（含 4 个人偶，Amazon 独家）":(59.99,"Amazon（Amazon 自营）","",True),
"Heeler 4WD 家庭车（含 4 个人偶）":(24.91,"Amazon（Amazon 自营）","",True),
"Heeler Family Road Trip 4WD（含 Chilli 人偶）":(17.99,"Kohl's",NC,False),
"Bingo's Helicopter 直升机（含 Bingo 人偶）":(14.99,"Amazon（Amazon 自营）","Walmart 搜索摘要显示 $14.00（未直接核实）",True),
"Family Figure 4-Pack（Bluey/Bingo/Bandit/Chilli）":(10.79,"Amazon（Amazon 自营）","Amazon Resale 二手 $9.71（包装轻度破损）",True),
"Garbage Truck 垃圾车（Bingo + Bin Man，Amazon 独家版）":(29.99,"Amazon（Amazon 自营）","无主报价，Amazon 自营报价预计 11-22 送达",True),
"Rescue Set 警车 + 消防车（含 3 个人偶）":(39.99,"Amazon（Amazon 自营）","标价 $49.99",True),
"Adventure Plane 飞机（含飞行员人偶）":(24.97,"Amazon","标价 $32.99；取自 Amazon 推荐栏",True),
"Pizza Girls 小车（含 Muffin 人偶）":(9.97,"Amazon",NC,False),
"Let's Play Chef Food Truck 餐车":(18.74,"Amazon","Typical $19.99；取自 Amazon 推荐栏",True),
"School Mates 人偶 4 件装（Jack/Pretzel/Mackenzie）":(29.99,"Amazon",NC,False),
"Here Come The Grannies 人偶 4 件装":(14.94,"Amazon",NC,False),
"Bingo's Claw Machine 抓娃娃机玩具组":(32.88,"Amazon",NC,False),
"Caravan Adventure 房车玩具组（含 Jean Luc）":(55.97,"Amazon",NC,False),
"3-in-1 Transforming Airplane 变形飞机（含 5 个人偶）":(79.99,"Amazon","取自 Amazon 推荐栏",True),
"Farmers Market 集市玩具组":(None,None,"今日价格未读取（Amazon 拦截）",False),
"Deluxe Play & Go 便携玩具组":(None,None,"今日价格未读取（Amazon 拦截）",False),
}
tracked=[]
for t in old["tracked_items"]:
    p,s,n,v=upd[t["name"]]
    t=dict(t); t["current_best"]={"price":p,"store":s,"note":n,"verified":v}
    if v: t["checked"]=D
    t["near_low"]=False
    h=t["historical_low"]
    if p is not None and h.get("price") and p<h["price"]:
        t["historical_low"]={"price":p,"store":s,"date":D,"source":"本次检查"}
    tracked.append(t)
if t["name"]=="Deluxe Play & Go 便携玩具组": pass
tracked.append(dict(name="Figure 4-Pack The Sleepover（Bluey/Bingo/Chilli/Muffin）",model="—",asin=None,
  current_best={"price":13.59,"store":"Amazon","note":"新增跟踪；取自 Amazon 推荐栏",
  "verified":True},historical_low={"price":None,"store":None,"date":None,"source":"未获得"},
  link="https://www.amazon.com/s?k=bluey+figure+4-pack+the+sleepover",checked=D,near_low=False))
state={"updated":D+"T09:55:00-05:00","supermarket_detail_2026-11-01":old.get("supermarket_detail_2026-11-01"),
 "threshold_supermarket_usd":30,"tracked_items":tracked,"alerts_sent":dict(old.get("alerts_sent",{}),**{D:[]})}
json.dump(state,open("state.json","w"),ensure_ascii=False,indent=1)

# LEGO
lego_hits=[
 ("42210","2 Fast 2 Furious Nissan Skyline GT-R (R34)",111.99,139.99,"$106.67（brickdiscounts：过去一年 Amazon 最低，未给日期；其价格图自 2025-05 起最低 $111.95）","+5.0%","https://www.amazon.com/s?k=LEGO+Technic+42210"),
 ("42214","Lamborghini Revuelto（预计年底退市）",151.99,189.99,"$149.95（brickdiscounts：过去一年 Amazon 最低，2026-10 内出现）","+1.4%","https://www.amazon.com/s?k=LEGO+Technic+42214"),
 ("42223","1966 Ford GT40 MKII",59.99,74.99,"$59.95（brickdiscounts：过去一年 Amazon 最低）","+0.1%","https://www.amazon.com/s?k=LEGO+Technic+42223"),
 ("42234","Dodge Viper GTS-R",51.99,64.99,"$51.95（brickdiscounts：过去一年 Amazon 最低）","+0.1%","https://www.amazon.com/s?k=LEGO+Technic+42234"),
 ("42229","Fast and Furious Mitsubishi Eclipse",51.99,64.99,"$50.77（brickdiscounts：过去一年 Amazon 最低）","+2.4%","https://www.amazon.com/s?k=LEGO+Technic+42229"),
 ("42227","Jeep Wrangler Rubicon",51.99,64.99,"$50.60（brickdiscounts：过去一年 Amazon 最低）","+2.7%","https://www.amazon.com/s?k=LEGO+Technic+42227"),
 ("42221","NASA Artemis Space Launch System Rocket",49.98,59.99,"$47.99（brickdiscounts：过去一年 Amazon 最低）","+4.1%","https://www.amazon.com/s?k=LEGO+Technic+42221"),
 ("42198","Bush Plane（LEGO.com 已售罄，预计 2026-12 退市）",22.49,27.99,"brickdiscounts 文字称年内最低 $22.35（2026-04），但其标题栏写过去一年最低 $19.99，数据自相矛盾；bricksvalue 记录最低 $22.04（Amazon，2026-10-18）","+0.6%～+12.5%（视采用的低价）","https://www.amazon.com/dp/B0DJ197ZQY"),
]
lold=json.load(open("lego_state_2026-11-02_backup.json"))
lego={"updated":D,"alerted":lold["alerted"]+[dict(set=s,name=n,store="Amazon（Amazon 自营，据 brickdiscounts/bricksvalue）",price=p,list=l,historical_low=h,link=k,date=D) for s,n,p,l,h,g,k in lego_hits],
 "checked_not_alerted":[
  {"set":"42204","price":35.49,"store":"Amazon","note":"已于 11-02 提醒，价格未再下降，今日不重复","date":D},
  {"set":"42209","price":83.99,"store":"LEGO.com","low":71.39,"low_store":"Target","low_date":"2026-10-05","src":"bricksvalue","date":D},
  {"set":"42226","price":51.99,"low":44.99,"src":"brickdiscounts","date":D},
  {"set":"42222","price":51.99,"low":45.99,"src":"brickdiscounts (eBay $47.99 第三方)","date":D},
  {"set":"42213","price":51.99,"low":45.00,"src":"brickdiscounts","date":D},
  {"set":"42212","price":51.99,"low":45.73,"src":"brickdiscounts","date":D},
  {"set":"42208","price":50.99,"low":31.49,"src":"brickdiscounts","date":D},
  {"set":"42154","price":95.99,"low":67.19,"src":"brickdiscounts","date":D},
  {"set":"42173","price":44.49,"low":39.99,"src":"brickdiscounts","date":D},
  {"set":"42219","price":27.95,"low":20.00,"src":"brickdiscounts","date":D},
  {"set":"42220","price":27.99,"low":24.99,"src":"brickdiscounts","date":D},
  {"set":"42211","price":88.50,"note":"历史低价未能获取（brickdiscounts 500 错误）","date":D},
  {"set":"42238","price":44.99,"note":"历史低价未能获取（brickdiscounts 500 错误）","date":D}]}
json.dump(lego,open("lego_state.json","w"),ensure_ascii=False,indent=1)

mold=json.load(open("mario_state_2026-11-02_backup.json"))
mi=mold["items"]
mi["B07KXNPVVW"].update(status="no featured offers (Amazon flags 'High price')",price=None,checked=D)
mi["B07KXT8D91"].update(status="page blocked today; 11-02 currently unavailable",price=None,checked=D)
mi["B07KXVBW38"].update(price=19.99,seller="third-party (from Amazon 'also viewed', only 1 left; not opened)",checked=D)
mi["B0FJY8QBP9"].update(price=16.99,seller="The Toys Store (FBA)",alerted=D,note="2026-11-03: no featured offer; Amazon.com not listed as featured; New (39) from $16.99",checked=D)
mi["B07KWXHZ1M"].update(price=11.00,seller="Summer B Store LLC (FBA); Amazon.com $11.69",checked=D)
mi["B07PGVZWSL"].update(price=11.49,seller="Just Family (FBA)",checked=D)
mi["B0CD3W263V"].update(status="currently unavailable (main offer); other offers on page ~$11.89-$18.84 not verified",price=None,checked=D)
mario={"updated":D,"items":mi,"alerted":mold["alerted"]+[{"asin":"B0FJY8QBP9","price":16.99,"date":D,"seller":"The Toys Store (FBA)"}]}
json.dump(mario,open("mario_state.json","w"),ensure_ascii=False,indent=1)

def money(x): return "—" if x is None else f"${x:.2f}"
rows=""
for t in tracked:
    c=t["current_best"]; h=t["historical_low"]
    cur=money(c["price"])+(f"（{c['store']}）" if c["store"] else "")+(f"<br><small>{html.escape(c['note'])}</small>" if c["note"] else "")
    low=(f"{money(h['price'])}（{h['store']}，{h['date']}）<br><small>{h['source']}</small>" if h["price"] else f"<small>{h['source']}</small>")
    rows+=f"<tr><td>{html.escape(t['name'])}<br><small>型号 {t['model']} {('ASIN '+t['asin']) if t['asin'] else ''}</small></td><td>{cur}</td><td>{low}</td><td><a href='{t['link']}'>链接</a></td></tr>\n"
lrows="".join(f"<tr><td>{s} {html.escape(n)}</td><td>Amazon（Amazon 自营）</td><td><b>${p:.2f}</b>（-{round((1-p/l)*100)}%）</td><td>${l:.2f}</td><td>{html.escape(h)}<br><small>距低价 {g}</small></td><td><a href='{k}'>Amazon</a></td></tr>\n" for s,n,p,l,h,g,k in lego_hits)
st="border-collapse:collapse;font-size:13px"
H=f"""<html><body style="font-family:Arial,sans-serif">
<h2>Bluey 玩具每日降价提醒 {D}</h2>
<p><small>检查时间：2026-11-03 上午约 9:40–9:55（美东时间，ET）。价格随时变动，下单前请以商家页面为准。</small></p>
<h3>一、今日处于或接近历史低价的 Bluey 商品（含超市玩具组 &lt; $30）</h3>
<p><b>今天没有。</b></p>
<p>超市玩具组（Moose 18918）今日最低在售新品价仍为 Amazon 自营 $42.49（Amazon Resale 二手 $39.09），未低于 $30；Kohl's 清仓价 $24.99 仍显示缺货。Slickdeals、Hip2Save 今日均无新的 Bluey 人偶玩具组优惠（过去的 $24.99–$29.99 帖子均已过期）。</p>
<h3>二、所有跟踪商品汇总</h3>
<table border="1" cellpadding="5" style="{st}">
<tr style="background:#eee"><th>商品</th><th>当前最低价（商家）</th><th>历史最低（价格、商家、日期、来源）</th><th>链接</th></tr>
{rows}</table>
<p><small>说明：camelcamelcamel 仍被拦截（403），Keepa 未能使用，因此多数商品的历史最低价无法核实，标为“未获得”。Amazon 对部分商品页拦截了自动访问，标注“沿用 11-02 价格”的商品今日未能重新核实；标注“推荐栏”的价格取自其他 Amazon 商品页的“顾客也看了”栏目，未逐一打开商品页核实卖家。</small></p>
<h3>三、LEGO Technic 优惠（今日新增，均在历史低价约 10% 以内）</h3>
<table border="1" cellpadding="5" style="{st}">
<tr style="background:#eee"><th>套装</th><th>商家</th><th>现价</th><th>原价</th><th>历史最低</th><th>链接</th></tr>
{lrows}</table>
<p><small>价格来自 brickdiscounts.com（标注为 Amazon 自营价，约 2–3 小时前检查）和 bricksvalue.com（11-03 更新），未逐一打开 Amazon 商品页核实；链接为 Amazon 搜索链接（42198 为商品页）。昨日已提醒的 42204 Toyota Supra 今日仍为 $35.49，未再降价，不重复列出。今天没有任何 Technic 套装折扣达到 35% 以上（42204 除外）。</small></p>
<h3>四、JAKKS 超级马里奥人偶</h3>
<table border="1" cellpadding="5" style="{st}">
<tr style="background:#eee"><th>商品</th><th>商家</th><th>现价</th><th>历史最低</th><th>链接</th></tr>
<tr><td>Rosalina 5 英寸（Super Mario Galaxy Movie 版，型号 432524，UPC 192995432529，ASIN B0FJY8QBP9）</td><td>第三方卖家 The Toys Store（Amazon 仓储配送）</td><td><b>$16.99</b>（比昨天提醒的 Amazon 自营 $19.97 更低；Amazon 自营今日不是主报价）</td><td>$19.95（Amazon，参考值）</td><td><a href="https://www.amazon.com/dp/B0FJY8QBP9">Amazon</a></td></tr>
</table>
<p><small>其他马里奥人偶今日均未达到提醒条件：Daisy 2.5 英寸无主报价（Amazon 标示“High price”）；Daisy 4 英寸页面今日被拦截，无法核实（昨日为无货）；Bowser Jr. 2.5 英寸（B0CD3W263V）主报价无货；Rosalina 2.5 英寸约 $19.99（第三方，仅剩 1 件）；Bowser Jr. 2.5 英寸（B07PGVZWSL）$11.49（第三方 Just Family）；Bowser Jr. 5 英寸 $11.00（第三方）/ $11.69（Amazon 自营），均高于历史低价 +15%。</small></p>
<p><small>来源：Amazon、Kohl's、Slickdeals、Hip2Save、DealCatcher、brickdiscounts.com、bricksvalue.com（均为英文来源）。</small></p>
</body></html>"""
open(f"email_{D}.html","w").write(H)
P=[f"Bluey 玩具每日降价提醒 {D}","检查时间：2026-11-03 上午约 9:40–9:55（美东时间，ET）。价格随时变动，下单前请以商家页面为准。","",
"一、今日处于或接近历史低价的 Bluey 商品（含超市玩具组 < $30）：今天没有。",
"超市玩具组今日最低在售新品价仍为 Amazon 自营 $42.49（二手 $39.09）；Kohl's 清仓价 $24.99 仍缺货。Slickdeals、Hip2Save 今日无新的 Bluey 人偶玩具组优惠。","","二、跟踪商品汇总："]
for t in tracked:
    c=t["current_best"];h=t["historical_low"]
    P.append(f"- {t['name']}：当前 {money(c['price'])} {c['store'] or ''} {c['note']}；历史最低 "+(f"{money(h['price'])}（{h['store']}，{h['date']}，{h['source']}）" if h['price'] else h['source'])+f"；{t['link']}")
P+=["","三、LEGO Technic（今日新增，均在历史低价约 10% 以内，Amazon 自营价，据 brickdiscounts/bricksvalue）："]
for s,n,p,l,h,g,k in lego_hits:
    P.append(f"- {s} {n}：${p:.2f}（原价 ${l:.2f}，-{round((1-p/l)*100)}%）；历史最低 {h}；距低价 {g}；{k}")
P+=["42204 Toyota Supra 仍为 $35.49，昨日已提醒，未再降价，不重复。","",
"四、超级马里奥：Rosalina 5 英寸（Galaxy Movie 版，432524，B0FJY8QBP9）第三方卖家 The Toys Store（Amazon 仓储配送）$16.99，低于昨日提醒的 $19.97 和参考历史低价 $19.95。https://www.amazon.com/dp/B0FJY8QBP9",
"其他马里奥人偶未达到提醒条件（详见 HTML 版）。","","说明：camelcamelcamel 被拦截，多数 Bluey 历史最低价未能核实；部分 Amazon 页面被拦截，相关商品沿用 11-02 价格。"]
open(f"email_{D}.txt","w").write("\n".join(P))
print("ok", len(tracked))
