import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from engine2 import *
P = panel(); market(P)
for n in ("V1_base", "V3_pierce_clx"): signals2(W.VARIANTS[n], n)
print("ok")
