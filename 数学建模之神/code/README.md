# 数学建模之神 代码说明
仅脚本，不含 PDF/数据文件。API 密钥通过环境变量 `GEMINI_API_KEY` 读取，无硬编码凭据。

## levin_bioelectric/（Levin 生物电综述文献核验）
- `cr.py`：读取 branchA/B 文献 CSV，逐条用 Crossref 校验 DOI 的标题相似度、年份、第一作者、期刊。
- `v.py`：按 DOI 快速查询 Crossref 元数据（单条核验）。
- `run_gai.py` / `run_gai_r2.py`：调用 Gemini(GoogleAI) 对综述草稿做第1/2轮交叉评审。

## multiscale_forces_papers/（多尺度力文献清单）
- `cr.py`：并发 Crossref 校验 meta.json 中所有 DOI（标题/年份/首作者）。
- `v.py` / `vr2.py` / `cq.py`：单条或批量 DOI 的 Crossref 查询与复核。
- `oa2.py`：用 Unpaywall 查找合法开放获取全文并下载 PDF。
- `dl.py`：解析检索结果 JSON，按 cite_key 下载可用 PDF 到 pdfs/。
- `ann.py`：文献注释表（尺度层级、方法、分级、一句话贡献）。
- `build.py`：汇总轮次/饱和度统计，生成清单与 scihub_needed.md（缺全文列表）。
- `fix2.py`：对 list.md 表格行做定点修正。
- `run_gai.py`：调用 Gemini 对文献清单做交叉核查。
