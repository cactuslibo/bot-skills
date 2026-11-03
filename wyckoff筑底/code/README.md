# wyckoff筑底 代码

威科夫（Wyckoff）吸筹结构可视化脚本。不含数据文件和密钥，运行前需要自备日线 CSV（列：date,open,high,low,close,volume）。

- `w.py`：画标准威科夫吸筹结构示意图（A–E 阶段、PS/SC/AR/ST/Spring/Test/SOS/LPS/BU）。
- `plot_crcl.py`：在 CRCL 真实日线上标注各阶段（第一版）。
- `plot_crcl_v2.py`：第二版，标签和配色与示意图统一，并画出待出现的 C/D 阶段示意路径。
- `report.py`：为每只候选股画威科夫标注图，合成多页 PDF 报告。

依赖：Python 3、pandas、matplotlib、Noto Sans CJK 字体。仅供研究参考，不构成投资建议。
