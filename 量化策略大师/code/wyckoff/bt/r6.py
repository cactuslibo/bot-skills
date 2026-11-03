from run2 import *
S = {}
for b in ("V1_base", "V3_pierce_clx"):
    for fn in ("base30", "dry", "rs", "mkt", "up200"):
        S[f"R6|{b}|E2|{fn}"] = (b, "E2", "none", F[fn])
run("R6", S)
