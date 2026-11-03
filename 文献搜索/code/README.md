# 文献搜索 · 辅助脚本

通用化脚本，配合 `../SKILL.md` 使用。所有邮箱参数均为占位符 `YOUR_EMAIL`（Crossref/Unpaywall/OpenAlex 礼貌池要求），请替换为你自己的邮箱。仅使用合法开放获取来源。

依赖：Python 3.8+、`curl`、`poppler-utils`（`pdfinfo` / `pdftotext`）。

输入清单统一为 CSV：`id,doi,title,year,first_author`

| 脚本 | 用途 | 用法 |
|---|---|---|
| `crossref_verify.py` | 用 Crossref 核验 DOI 对应的标题/年份/第一作者，标出 TITLE/YEAR/AUTHOR 不一致 | `python crossref_verify.py refs.csv --email YOUR_EMAIL` |
| `oa_download.py` | 依次查询 Unpaywall、OpenAlex、Semantic Scholar、Europe PMC、arXiv、bioRxiv/medRxiv 的 OA 链接并下载 PDF；校验 `%PDF` 文件头、`pdfinfo`、首页标题匹配 | `python oa_download.py refs.csv --outdir pdfs --email YOUR_EMAIL` |
| `validate_pdfs.sh` | 批量校验目录内 PDF，损坏/伪 PDF（HTML 登录页等）移入 `bad/` | `bash validate_pdfs.sh pdfs` |
| `package_zip.py` | 打包 PDF 为 zip，超过大小上限自动分卷 | `python package_zip.py pdfs --name papers --max-mb 20` |
| `build_list.py` | 合并核验与下载结果，生成 Markdown 文献清单 | `python build_list.py --refs refs.csv --check crossref_check.csv --dl oa_results.csv` |

典型流程：整理 refs.csv → `crossref_verify.py` → `oa_download.py` → `validate_pdfs.sh` → `package_zip.py` → `build_list.py`
