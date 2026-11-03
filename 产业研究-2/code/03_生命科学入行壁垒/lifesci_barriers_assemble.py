import os
ver=open("_verify.md").read() if os.path.exists("_verify.md") else "## 核验结论\n\n### Crossref\n见步骤 4。\n\n### GoogleAI 引用核验\n**GoogleAI 核验待做**（调用进行中/失败，原因见 run_gai.log）。\n"
n=len([f for f in os.listdir("pdfs") if f.endswith(".pdf")])
pdf=f"""## 全文情况
- pdfs/ 现有 **{n} 个 PDF**（均以 `%PDF-` 开头且 pdfinfo 可读）：第 1 版本 bot 下载 9 个；SciHub bot 下载并合并 16 个（B04、B14、B18、B20、B24、B26、B30、B32、B33、B36、B37、B38、B39、B41、B43、B45，抽查首页题名与 ID 对应）；本轮新增 14 个（Undermind 13 个：B46、B50、B53、B58、B61、B62、B67、B70、B72、B81、B84、B85、B86；NBER 1 个：B51）。
- 第 1 版仍缺 PDF 的 20 篇：B01、B02、B03、B05、B07、B08、B09、B10、B11、B15、B17、B19、B23、B27、B28、B31、B34、B35、B42、B44。
- 本轮新增缺 PDF 的 28 篇：见 `/workspace/lifesci_barriers/scihub_needed_round2.md`。其中 B47（Wiley）、B49（Clin Ther）、B74（Emerald）有出版社 OA 链接但被反爬拦截；B78 在 PMC4290669 有作者手稿，PMC 返回反爬页面。
"""
s="\n\n".join([open("_head.md").read(),open("_summary.md").read(),open("_old_tables.md").read(),open("_cro_table.md").read(),open("_method.md").read(),ver,pdf])
open("lit.md","w").write(s); print(len(s))
