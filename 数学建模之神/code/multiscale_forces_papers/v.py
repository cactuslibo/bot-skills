import json,urllib.request,re
def g(d):
    try:
        m=json.load(urllib.request.urlopen(urllib.request.Request("https://api.crossref.org/works/"+d,headers={"User-Agent":"mailto:a@b.c"}),timeout=30))["message"]
        return f"{(m.get('title') or [''])[0][:80]} | {(m.get('container-title') or [''])[0][:40]} | {m.get('issued',{}).get('date-parts')} | {[a.get('family') for a in m.get('author',[])][:7]} | {m.get('volume')} {m.get('page')}"
    except Exception as e: return "ERR "+str(e)
for d in "10.1393/ncr/i2014-10098-1 10.1137/23M1553315 10.1103/PhysRevLett.114.198301 10.1021/acs.chemrev.2c00586 10.1021/chemrev.2c00586 10.1098/rstb.1952.0012 10.1093/acprof:oso/9780198567295.001.0001 10.1088/0370-1328/85/4/301 10.1143/PTP.33.423 10.1103/PhysRev.124.983 10.1063/1.1731409 10.1080/00018737900101365 10.1063/1.478705 10.1063/1.1740347 10.1002/pol.1958.1203312618 10.1016/0079-6816(93)90013-L 10.1021/j150453a001 10.1070/PU1961v004n02ABEH003330 10.1080/00018736100101281 10.1016/0378-4371(79)90223-1 10.1103/PhysRevB.4.3174 10.1016/0370-1573(74)90023-4 10.1126/science.1172046 10.1146/annurev-cellbio-100913-013325 10.1103/PhysRevLett.75.1226 10.1103/RevModPhys.49.435 10.1063/1.2998601 10.1063/2.0000001 10.1063/1.2938860".split():
    print(d,"=>",g(d))
