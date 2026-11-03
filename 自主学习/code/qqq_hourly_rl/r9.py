"""Round 9：H5 = H2（涨跌家数反转）∪ H3（盘中 VIX 反转）的并集信号，共享 3 个参数（rp、z、y_breadth；VIX 回落阈值固定 4%）。
（原计划的 H6 动态出场未实现，本轮只有 H5 一个族 36 个候选。）
**污染说明**：方向直接来自第 8 轮验证集结果（H2、H3 满足第 1–6 条），属于看过验证集之后的设计。训练 2015–2021（VIX 分支只在 2020 起生效）。"""
import itertools, numpy as np, pandas as pd
from r8 import M8, triggers
class M9(M8):
    def sigH5(s,rp,z,y):
        with np.errstate(invalid='ignore'):
            a=np.nan_to_num(s.sigH2(rp,z,y)).astype(bool); b=np.nan_to_num(s.sigH3(rp,0.04,z)).astype(bool)
        return a|b
M=M9
def cands():
    C=[]
    for rp,z,y in itertools.product([15,20,30,40],[0.55,0.6,0.65],[0.003,0.006,0.01]): C.append(('H5_union',dict(rp=rp,z=z,y=y)))
    return C
def build(m,fam,p):
    if fam=='P2': return m.p2()[:2]
    if fam=='H5_union': return m.overlay(m.sigH5(**p))
TRAIN={'H5_union':('2015-01-01','2022-01-01')}
