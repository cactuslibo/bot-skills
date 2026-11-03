from run2 import *
S = {}
for b in ("V1_base", "V3_pierce_clx"):
    for ex in ("none", "intra0", "intra_atr1", "intra_atr2", "close0"):
        S[f"R5|{b}|E2|{ex}"] = (b, "E2", ex, None)
run("R5", S)
