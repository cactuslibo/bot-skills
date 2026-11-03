import json,urllib.request,urllib.parse,sys
def g(u):
    return json.load(urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"mailto:a@b.c"}),timeout=30))
for doi in ["10.1201/b15597-19","10.1021/acspolymersau.2c00049","10.1063/1.1744102","10.1002/9781118788295.ch3"]:
    try:
        m=g("https://api.crossref.org/works/"+doi)["message"]; print(doi,"|",m.get("title"),"|",m.get("container-title"),m.get("issued"),[a.get("family") for a in m.get("author",[])][:4])
    except Exception as e: print(doi,"ERR",e)
for q in ["Denton Coarse-grained modeling of charged colloidal suspensions Poisson-Boltzmann effective interactions",
 "Likos Colloidal interactions from effective potentials to structure","Brader Statistical mechanics of inhomogeneous model colloid-polymer mixtures",
 "Boudaoud Kiss Ptashnyk Multiscale modelling and analysis of growth of plant tissues","McNamara Synthetic physiology manipulating measuring biological pattern formation light",
 "Solon Pressure is not a state function for generic active fluids","Solon Tailleur equation of state for active matter","Cahn Hilliard Free energy of a nonuniform system interfacial free energy 1958"]:
    for it in g("https://api.crossref.org/works?rows=3&query.bibliographic="+urllib.parse.quote(q))["message"]["items"]:
        print(" ",q[:25],"->",it["DOI"],"|",(it.get("title") or [""])[0][:90],"|",(it.get("container-title") or [""])[0][:40],it.get("issued",{}).get("date-parts"))
