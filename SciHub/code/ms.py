import csv,json,dvc_lib as L
from concurrent.futures import ThreadPoolExecutor
L.D='/workspace/multiscale_forces_papers/pdfs'
rows=list(csv.reader(open('ms.tsv'),delimiter='\t'))
with ThreadPoolExecutor(8) as ex: r=list(ex.map(L.run,rows))
json.dump(r,open('res_ms.json','w'))
for x in r: print(x)
