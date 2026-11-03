import json, html
D="2026-11-02"
items=[
 # name, model, asin, cur_price, cur_store, cur_note, low_price, low_store, low_date, low_src, link, verified
 ("Let's Play Chef 超市玩具组（Supermarket Playset）","18918","B0DQ6R6CXX",42.49,"Amazon（Amazon 自营）","Amazon Resale 二手 $39.09；Kohl's 清仓价 $24.99 但缺货；Target 价格未能读取",24.99,"Target","2026-09-07","Hip2Save（已过期）","https://www.amazon.com/dp/B0DQ6R6CXX",True),
 ("Cruise Ship 邮轮玩具组（含 Bluey、Bingo）","19850","B0GFXMLVWS",56.99,"Amazon","取自 Amazon 搜索页，卖家未核实；标价 $64.99",25.00,"Amazon / Walmart","2026-09-20（Amazon）；2026-10-04、10-11（Walmart）","Ben's Bargains / Slickdeals（均已过期）","https://www.amazon.com/dp/B0GFXMLVWS",True),
 ("Mega Bundle 家庭房屋 + BBQ（含 4 个人偶，Amazon 独家）","13073","B088MXQW9L",59.99,"Amazon","取自 Amazon 搜索页",49.99,"Amazon","2023-10-11","DealAM（已过期）","https://www.amazon.com/dp/B088MXQW9L",True),
 ("Heeler 4WD 家庭车（含 4 个人偶）","17637","B0BQNTBR71",24.91,"Amazon","取自 Amazon 搜索页",None,None,None,"未获得（camelcamelcamel 被拦截）","https://www.amazon.com/dp/B0BQNTBR71",True),
 ("Heeler Family Road Trip 4WD（含 Chilli 人偶）","17661",None,17.99,"Kohl's","来自搜索摘要，未直接核实",5.99,"Amazon","2025-11-05","Slickdeals（已过期）","https://www.kohls.com/product/prd-7034176/bluey-s11-heeler-family-road-trip-4wd-vehicle.jsp",False),
 ("Bingo's Helicopter 直升机（含 Bingo 人偶）","17560","B0BQSH412F",14.99,"Amazon（Amazon 自营）","Walmart 搜索摘要显示 $14.00（未直接核实）",None,None,None,"未核实（有社交媒体称 2026-08 Walmart $11.99，非可靠来源）","https://www.amazon.com/dp/B0BQSH412F",True),
 ("Family Figure 4-Pack（Bluey/Bingo/Bandit/Chilli）","—","B083XNCRS3",10.79,"Amazon","取自 Amazon 搜索页",None,None,None,"未获得（Slickdeals 2025-05-14 的 $8.51 为 Family Trip 4-Pack，不同款）","https://www.amazon.com/dp/B083XNCRS3",True),
 ("Garbage Truck 垃圾车（Bingo + Bin Man，Amazon 独家版）","—","B0CJK7F677",29.99,"Amazon","取自 Amazon 搜索页",None,None,None,"未获得（Hip2Save 2024 年 $9.73 为旧版 Bluey + Bin Man，不同款）","https://www.amazon.com/dp/B0CJK7F677",True),
 ("Rescue Set 警车 + 消防车（含 3 个人偶）","—","B0GNCFRP64",39.99,"Amazon","Amazon 标示 Typical $49.99",None,None,None,"未核实（有社交媒体称 2026-10-12 $24.99，非可靠来源）","https://www.amazon.com/dp/B0GNCFRP64",True),
 ("Adventure Plane 飞机（含飞行员人偶）","19334",None,24.99,"Amazon","标价 $32.99",None,None,None,"未获得","https://www.amazon.com/s?k=bluey+adventure+plane",True),
 ("Pizza Girls 小车（含 Muffin 人偶）","—",None,9.97,"Amazon","标价 $10.99",None,None,None,"未获得","https://www.amazon.com/s?k=bluey+pizza+girls+car",True),
 ("Let's Play Chef Food Truck 餐车","—",None,18.74,"Amazon","Typical $19.99",None,None,None,"未获得","https://www.amazon.com/s?k=bluey+food+truck+playset",True),
 ("School Mates 人偶 4 件装（Jack/Pretzel/Mackenzie）","—",None,29.99,"Amazon","Typical $36.90；仅剩 1 件",None,None,None,"未获得","https://www.amazon.com/s?k=bluey+school+mates+figure+4+pack",True),
 ("Here Come The Grannies 人偶 4 件装","—",None,14.94,"Amazon","",None,None,None,"未获得","https://www.amazon.com/s?k=bluey+here+come+the+grannies+4+pack",True),
 ("Bingo's Claw Machine 抓娃娃机玩具组","—",None,32.88,"Amazon","",None,None,None,"未获得","https://www.amazon.com/s?k=bluey+claw+machine+playset",True),
 ("Caravan Adventure 房车玩具组（含 Jean Luc）","—",None,55.97,"Amazon","",None,None,None,"未获得","https://www.amazon.com/s?k=bluey+caravan+adventure+playset",True),
 ("3-in-1 Transforming Airplane 变形飞机（含 5 个人偶）","—",None,79.99,"Amazon","",None,None,None,"未获得","https://www.amazon.com/s?k=bluey+3-in-1+transforming+airplane",True),
 ("Farmers Market 集市玩具组","17555","B0CCWT2CKF",None,None,"今日价格未读取",None,None,None,"未获得","https://www.amazon.com/dp/B0CCWT2CKF",False),
 ("Deluxe Play & Go 便携玩具组","—","B08S3B21W4",None,None,"今日价格未读取",None,None,None,"未获得","https://www.amazon.com/dp/B08S3B21W4",False),
]
old=json.load(open("state.json"))
tracked=[]
for n,m,a,cp,cs,note,lp,ls,ld,lsrc,link,v in items:
    tracked.append(dict(name=n,model=m,asin=a,current_best={"price":cp,"store":cs,"note":note,"verified":v},
      historical_low={"price":lp,"store":ls,"date":ld,"source":lsrc},link=link,checked=D,
      near_low=False))
state={"updated":D+"T09:55:00-05:00","supermarket_detail_2026-11-01":old,"threshold_supermarket_usd":30,
 "tracked_items":tracked,"alerts_sent":{D:[]}}
json.dump(state,open("state.json","w"),ensure_ascii=False,indent=1)
lego={"updated":D,"alerted":[{"set":"42204","name":"Fast and Furious Toyota Supra MK4","store":"Amazon (sold by Amazon)","price":35.49,"list":59.99,"historical_low":"$33.63 (brickdiscounts: lowest at Amazon past year, date not shown); chart min since Feb 2025 $35.49; riverprice: ATL $35.49 2026-10-17","link":"https://www.amazon.com/dp/B0DJ197M66","date":D}],
 "checked_not_alerted":[{"set":"42209","price":83.99,"store":"LEGO.com","low":71.39,"low_store":"Target","low_date":"2026-10-05","src":"bricksvalue"}]}
json.dump(lego,open("lego_state.json","w"),ensure_ascii=False,indent=1)
mario={"updated":D,"items":{
 "B07KXNPVVW":{"name":"Daisy 2.5in","low":5.66,"status":"no featured offers (Amazon flags 'High price')","price":None},
 "B07KXT8D91":{"name":"Daisy 4in","low":9.99,"status":"currently unavailable","price":None},
 "B07KXVBW38":{"name":"Rosalina 2.5in","low":9.54,"price":19.99,"seller":"Just Family (FBA)"},
 "B0FJY8QBP9":{"name":"Rosalina 5in Galaxy Movie 432524","low":19.95,"price":19.97,"seller":"Amazon.com","alerted":D,"note":"Amazon Resale used $16.39; Entertainment Earth $24.99 sold out"},
 "B07KWXHZ1M":{"name":"Bowser Jr 5in Galaxy Movie paintbrush","low":5.84,"price":11.58,"seller":"Amazon.com"},
 "B07PGVZWSL":{"name":"Bowser Jr 2.5in","low":7.95,"price":11.68,"seller":"Just Family (FBA)"},
 "B0CD3W263V":{"name":"Bowser Jr 2.5in (95778)","low":None,"status":"currently unavailable","price":None}},
 "alerted":[{"asin":"B0FJY8QBP9","price":19.97,"date":D}]}
json.dump(mario,open("mario_state.json","w"),ensure_ascii=False,indent=1)

def money(x): return "—" if x is None else f"${x:.2f}"
rows=""
for t in tracked:
    c=t["current_best"]; h=t["historical_low"]
    cur=money(c["price"])+(f"（{c['store']}）" if c["store"] else "")+(f"<br><small>{html.escape(c['note'])}</small>" if c["note"] else "")
    low=(f"{money(h['price'])}（{h['store']}，{h['date']}）<br><small>{h['source']}</small>" if h["price"] else f"<small>{h['source']}</small>")
    rows+=f"<tr><td>{html.escape(t['name'])}<br><small>型号 {t['model']} {('ASIN '+t['asin']) if t['asin'] else ''}</small></td><td>{cur}</td><td>{low}</td><td><a href='{t['link']}'>链接</a></td></tr>\n"
st="border-collapse:collapse;font-size:13px"
H=f"""<html><body style="font-family:Arial,sans-serif">
<h2>Bluey 玩具每日降价提醒 {D}</h2>
<p><small>检查时间：2026-11-02 上午约 9:45–10:00（美东时间，ET）。价格随时变动，下单前请以商家页面为准。</small></p>
<h3>一、今日处于或接近历史低价的 Bluey 商品（含超市玩具组 &lt; $30）</h3>
<p><b>今天没有。</b></p>
<p>超市玩具组（Moose 18918）今日最低在售新品价为 Amazon 自营 $42.49（Amazon Resale 二手 $39.09），未低于 $30；Kohl's 清仓价 $24.99 但显示缺货，无法购买。</p>
<h3>二、所有跟踪商品汇总</h3>
<table border="1" cellpadding="5" style="{st}">
<tr style="background:#eee"><th>商品</th><th>当前最低价（商家）</th><th>历史最低（价格、商家、日期、来源）</th><th>链接</th></tr>
{rows}</table>
<p><small>说明：camelcamelcamel 被拦截（403/Cloudflare），Keepa 未能使用，因此多数商品的历史最低价无法核实，标为“未获得”；标注“搜索页”的价格取自 Amazon 搜索结果页，未逐一打开商品页核实卖家。“链接”为搜索链接的商品，今日未取得确切的商品页 ASIN。</small></p>
<h3>三、LEGO Technic 优惠</h3>
<table border="1" cellpadding="5" style="{st}">
<tr style="background:#eee"><th>套装</th><th>商家</th><th>现价</th><th>原价</th><th>历史最低</th><th>链接</th></tr>
<tr><td>42204 Fast and Furious Toyota Supra MK4（810 片，预计 2026-12-31 前退市）</td><td>Amazon（Amazon 自营，有货）</td><td><b>$35.49</b>（-41%）</td><td>$59.99</td><td>brickdiscounts：过去一年 Amazon 最低 $33.63（未给出日期）；其价格图自 2025-02 起记录的最低值为 $35.49。现价距 $33.63 约 +5.5%</td><td><a href="https://www.amazon.com/dp/B0DJ197M66">Amazon</a></td></tr>
</table>
<h3>四、JAKKS 超级马里奥人偶</h3>
<table border="1" cellpadding="5" style="{st}">
<tr style="background:#eee"><th>商品</th><th>商家</th><th>现价</th><th>历史最低</th><th>链接</th></tr>
<tr><td>Rosalina 5 英寸（Super Mario Galaxy Movie 版，型号 432524，UPC 192995432529，ASIN B0FJY8QBP9）</td><td>Amazon（Amazon 自营，有货）</td><td><b>$19.97</b>（Amazon Resale 二手 $16.39，仅 1 件，可能无原包装）</td><td>$19.95（Amazon，参考值）</td><td><a href="https://www.amazon.com/dp/B0FJY8QBP9">Amazon</a></td></tr>
</table>
<p><small>其他马里奥人偶今日均未达到提醒条件：Daisy 2.5 英寸、Daisy 4 英寸、Bowser Jr. 2.5 英寸（B0CD3W263V）无货或无主要报价；Rosalina 2.5 英寸 $19.99、Bowser Jr. 2.5 英寸（B07PGVZWSL）$11.68 均为第三方卖家；Bowser Jr. 5 英寸 $11.58（Amazon 自营），高于历史低价 $5.84 的 +15%。</small></p>
<p><small>来源：Amazon、Kohl's、Slickdeals、Hip2Save、Ben's Bargains、DealAM、bricksvalue.com、brickdiscounts.com、Entertainment Earth（均为英文来源）。</small></p>
</body></html>"""
open("email_2026-11-02.html","w").write(H)
# plain text
P=[f"Bluey 玩具每日降价提醒 {D}","检查时间：2026-11-02 上午约 9:45–10:00（美东时间，ET）。","","一、今日处于或接近历史低价的 Bluey 商品（含超市玩具组 < $30）：今天没有。","超市玩具组今日最低在售新品价为 Amazon 自营 $42.49（二手 $39.09）；Kohl's 清仓价 $24.99 但缺货。","","二、跟踪商品汇总："]
for t in tracked:
    c=t["current_best"];h=t["historical_low"]
    P.append(f"- {t['name']}：当前 {money(c['price'])} {c['store'] or ''} {c['note']}；历史最低 "+(f"{money(h['price'])}（{h['store']}，{h['date']}，{h['source']}）" if h['price'] else h['source'])+f"；{t['link']}")
P+=["","三、LEGO Technic：42204 Toyota Supra MK4，Amazon 自营 $35.49（原价 $59.99，-41%），历史最低：brickdiscounts 称过去一年 $33.63（未给日期）。https://www.amazon.com/dp/B0DJ197M66","","四、超级马里奥：Rosalina 5 英寸（Galaxy Movie 版，432524），Amazon 自营 $19.97，历史最低 $19.95。https://www.amazon.com/dp/B0FJY8QBP9","","说明：camelcamelcamel 被拦截，多数历史最低价未能核实。"]
open("email_2026-11-02.txt","w").write("\n".join(P))
