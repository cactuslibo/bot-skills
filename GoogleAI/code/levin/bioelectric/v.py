import json,urllib.request,urllib.parse
def cr(d):
  try:
    m=json.load(urllib.request.urlopen(urllib.request.Request("https://api.crossref.org/works/"+d,headers={"User-Agent":"r (mailto:x@example.com)"}),timeout=30))["message"]
    return f"{d} | {(m.get('author') or [{}])[0].get('family')} {m['issued']['date-parts'][0][0]} | {(m.get('container-title') or [''])[0]} | {m['title'][0][:110]}"
  except Exception as e: return f"{d} NOTFOUND {e}"
for d in ["10.1073/pnas.0906823106","10.1016/j.celrep.2013.07.022","10.1242/dev.100560","10.1016/j.cub.2006.10.067","10.1038/s41467-022-34204-9","10.1016/j.bbamem.2005.09.007","10.1523/JNEUROSCI.5607-09.2010","10.1083/jcb.200207106","10.1242/dev.142034","10.1038/ncb2659","10.1074/jbc.M211609200","10.1113/jphysiol.2008.163097"]: print(cr(d))
def ab(d):
  u="https://www.ebi.ac.uk/europepmc/webservices/rest/search?format=json&resultType=core&query="+urllib.parse.quote(f'DOI:"{d}"')
  r=json.load(urllib.request.urlopen(u,timeout=30))["resultList"]["result"]
  return r[0].get("abstractText","")[:1500] if r else "none"
for d in ["10.1038/s41467-022-34363-w","10.1038/s41467-026-76758-z","10.1038/s41567-019-0765-4","10.15252/embr.202051861","10.1016/j.bpj.2017.04.011","10.1002/jcp.29290"]: print("\n##",d,ab(d))
