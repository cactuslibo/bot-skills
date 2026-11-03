import json,os,re
from collections import Counter,defaultdict
W="/workspace/bottleneck_metric/lit_work"
inc=json.load(open(f"{W}/included.json"))
exec(open(f"{W}/r2/grades.py").read()); exec(open(f"{W}/r3/grades_r3.py").read())
X2=json.load(open(f"{W}/r2/crossref_r2.json")); I2=json.load(open(f"{W}/r2/info_new.json"))
X3=json.load(open(f"{W}/r3/crossref_r3.json")); I3=json.load(open(f"{W}/r3/info_r3.json"))
md=open("/workspace/bottleneck_metric/lit_from_wenxian_v2.md").read()
M={}
# round0 from v1 table
rows={m.group(1):[c.strip() for c in m.group(0).split('|')[1:-1]] for m in re.finditer(r'^\| (\w+) \| .+\|$',md,re.M)}
for k,v in inc.items():
    M[k]=dict(key=k,branch=v[0],use=v[1],cred=v[2],ind=v[3],note=v[4],stage="R0")
# r2
for k,v in G.items():
    x=X2.get(k,{}); i=I2.get(k,{})
    M[k]=dict(key=k,branch=v[0],use=v[1],cred=v[2],ind=v[3],note=v[4],stage=v[5],title=x.get("cr_title") or i.get("title"),authors=x.get("cr_authors") or i.get("authors"),year=x.get("cr_year") or i.get("year"),venue=x.get("cr_container") or i.get("venue"),doi=x.get("formal_doi") or x.get("cr_doi") or i.get("doi"),xstatus=x.get("status"),xnote=x.get("note",""))
FORM3={"Kei19":("10.1093/icc/dty014","Industrial and Corporate Change","2019（在线 2018）"),"Can13":("10.1016/j.jeconbus.2012.11.002","Journal of Economics and Business","2013"),"Ste08":("10.3790/aeq.54.4.231","Applied Economics Quarterly","2008"),"Hor07":("10.1596/1813-9450-4284","World Bank Policy Research WP 4284","2007"),"Akt12":("10.1016/j.jbankfin.2011.12.001","Journal of Banking & Finance","2012"),"Nor12b":("10.1111/j.1468-036x.2010.00561.x","European Financial Management","2012（Crossref issued 2010）"),"Ekl19":("10.1007/s10663-018-9399-5","Empirica","2019（Crossref issued 2018）"),"Lin20e":("10.1080/00036846.2019.1621982","Applied Economics","2020（Crossref issued 2019）")}
for k,v in G3.items():
    x=X3[k]; i=I3[k]; bd=x.get("by_doi") if isinstance(x.get("by_doi"),dict) and x["by_doi"].get("doi") else None
    doi=(bd or {}).get("doi") or i.get("doi"); venue=(bd or {}).get("venue") or i.get("venue"); yr=(bd or {}).get("year") or i.get("year")
    xs="ok" if bd and bd["sim"]>=0.6 else "unverified"
    if k in FORM3: doi,venue,yr=FORM3[k]; xs="ok-formal"
    if k in ("Ger90","Khe90"): venue="Mueller (ed.) The Dynamics of Company Profits, CUP 1990（书章）"
    note=""
    if k=="Mon13": note="疑似正式版：Montez, Ruiz-Aliseda & Ryall 2018 Management Science 10.1287/mnsc.2017.2737（题名不同，未确认同一文）"
    if k=="She18c": note="疑似后续正式版：She, Wei & You 2026 Management Science 10.1287/mnsc.2024.04715（题名不同，未确认）"
    if k=="Zho16": note="无 DOI；Crossref 有相近题名 Zhong, Wang & Zhou 2017 Asian Review of Accounting 10.1108/ara-11-2015-0118（作者不完全一致，未确认）"
    M[k]=dict(key=k,branch=v[0],use=v[1],cred=v[2],ind=v[3],note=v[4],stage=v[5],title=i["title"],authors=i["authors"],year=yr,venue=venue,doi=doi,xstatus=xs,xnote=note)
# Tae12 -> Jac15 replacement (same paper)
if "Tae12" in M:
    t=M.pop("Tae12"); t["key"]="Jac15"; t["title"]="Kingpins, Bottlenecks, and Value Dynamics Along a Sector"; t["authors"]="Michael G. Jacobides, C. Jennifer Tae"; t["year"]=2015; t["venue"]="Organization Science 26(3):889–907"; t["doi"]="10.1287/orsc.2014.0958"; t["cred"]=2; t["xnote"]="原 Undermind 条目 Tae12（AOM 2012 会议版）已并入正式版"; M["Jac15"]=t
D="/workspace/bottleneck_metric/lit_pdfs"
files=os.listdir(D)
def pdf(k):
    k2="Tae12" if k=="Jac15" else k
    f=[x for x in files if re.match(re.escape(k)+r'(\.|_)',x) or re.match(re.escape(k2)+r'(\.|_)',x)]
    return f[0] if f else None
for k in M: M[k]["pdf"]=pdf(k)
json.dump(M,open("master.json","w"),ensure_ascii=False,indent=1)
orphan=[f for f in files if re.match(r'([A-Za-z]+\d{2}[a-z]{0,3})',f).group(1) not in M]
print("total",len(M),"orphan pdf",orphan,"pdf files",len(files),"with pdf",sum(1 for k in M if M[k]["pdf"]))
c=Counter((v["stage"]) for v in M.values()); print(c)
AB=lambda s:[k for k,v in M.items() if v["stage"]==s and v["use"] in "AB"]
order=["R0","L","S1","S2","S3","S4","S5","S6","S7","R1","R2","R3","R4","R5","G1","G2"]
for s in order: print(s,len([k for k,v in M.items() if v["stage"]==s]),"AB",len(AB(s)))
