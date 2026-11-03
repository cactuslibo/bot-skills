from run2 import *
S = {}
for b in ("V1_base", "V3_pierce_clx"):
    S[f"R7|{b}|LPS|none"] = (b, "LPS", "none", None)
    S[f"R7|{b}|LPS|up200"] = (b, "LPS", "none", F["up200"])
run("R7", S)
