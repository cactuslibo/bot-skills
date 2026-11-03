import json,urllib.request,urllib.parse
UA={"User-Agent":"lit-check/1.0 (mailto:YOUR_EMAIL@example.com)"}
import time
def q(t,a):
    time.sleep(3)
    u=f"https://api.crossref.org/works?query.bibliographic={urllib.parse.quote(t)}&query.author={urllib.parse.quote(a)}&rows=3&select=DOI,title,issued,author,container-title,volume,page"
    for i in range(5):
        try:
            j=json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=40)); break
        except Exception as e: time.sleep(10)
    return [{"doi":m["DOI"],"title":(m.get("title") or [""])[0],"year":m["issued"]["date-parts"][0][0],"c":(m.get("container-title") or [""])[0],"v":m.get("volume"),"p":m.get("page"),"au":[x.get("family") for x in m.get("author",[])]} for m in j["message"]["items"]]
Q={"Irv13":("Customer-base concentration, profitability, and the relationship life cycle","Irvine"),
"War96":("Industry differences in the persistence of firm-specific returns","Waring"),
"Ben01":("Oscillate wildly: asymmetries and persistence in company-level profitability","Benito"),
"Gof13":("Profitability, trade credit and institutional structure of production","Gofman"),
"Ace11":("The network origins of aggregate fluctuations","Acemoglu"),
"Sin21b":("Asymmetrical Power Relationships in Supply Chain Networks","Singh"),
"GAP_Mueller77":("The persistence of profits above the norm","Mueller"),
"GAP_Mueller86":("Profits in the long run","Mueller"),
"GAP_Antras12":("Measuring the upstreamness of production and trade flows","Antras"),
"GAP_NovyMarx13":("The other side of value: The gross profitability premium","Novy-Marx"),
"GAP_FeeThomas04":("Sources of gains in horizontal mergers: evidence from customer, supplier, and rival firms","Fee"),
"GAP_AhernHarford14":("The importance of industry links in merger waves","Ahern"),
"GAP_Farrell19":("Weaponized interdependence: how global economic networks shape state coercion","Farrell"),
"GAP_Baldwin14":("The smile curve: evolving sources of value added in manufacturing","Baldwin"),
"GAP_Ye15":("Measuring smile curves in global value chains","Ye"),
"GAP_BaqaeeFarhi19":("The macroeconomic impact of microeconomic shocks: beyond Hulten's theorem","Baqaee"),
}
out={k:q(*v) for k,v in Q.items()}
json.dump(out,open("crossref_extra.json","w"),ensure_ascii=False,indent=1)
for k,v in out.items():
    print(k); [print("   ",x["doi"],x["year"],x["c"][:40],x["v"],x["p"],",".join(filter(None,x["au"][:4])),"|",x["title"][:70]) for x in v]
