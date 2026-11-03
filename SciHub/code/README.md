# SciHub bot 文献下载与校验代码

> 仅使用合法开放获取（OA）来源：Unpaywall、OpenAlex、arXiv、Semantic Scholar、Europe PMC / PMC、NBER、机构仓储（如 DukeSpace）、OSTI 等。**不使用 Sci-Hub。**
> 下载后用 `pdftotext`（poppler-utils）抽取文本并比对标题，确认 PDF 有效、内容正确。

## 环境
```bash
pip install requests        # 部分脚本仅用标准库 urllib
sudo apt install poppler-utils
export UNPAYWALL_EMAIL=you@example.com   # Unpaywall/OpenAlex 礼貌池要求的联系邮箱
```

## 脚本说明
| 文件 | 用途 | 用法 |
|---|---|---|
| `fetch.py` | 主下载器：按 DOI/标题依次查 Unpaywall → OpenAlex → Semantic Scholar → arXiv → Europe PMC，下载 PDF 并用 pdftotext 校验 | 读 `items.tsv`；`python3 fetch.py <tag>` → `res_<tag>.json` |
| `dvc_lib.py` | 共享函数库（OA 查询、下载、PDF 校验） | 被其他脚本 import |
| `dvc.py` | 批量下载一个清单（`dvc.tsv`）的首轮 | `python3 dvc.py` → `res_dvc.json` |
| `dvc2.py` / `dvc3.py` | 针对首轮失败条目补下（PMC、NBER、OpenAlex 备用位置） | 首轮后运行 |
| `duke.py` | 从机构仓储（DukeSpace）补下 | `python3 duke.py` |
| `ms.py`–`ms4.py` | 另一清单（`ms.tsv`）的多轮补下（OpenAlex、arXiv、S2） | 依次运行 |
| `r4.py` / `r5.py` | 从 Markdown 文献列表解析条目并重试 arXiv / S2 / NBER | `python3 r4.py <list.md> <out.json>` |
| `todo.py` | 从结果 JSON 生成未完成清单 | `python3 todo.py res.json todo.tsv` |

清单文件（`*.tsv`）为 `标题<TAB>DOI` 格式，需自行准备；结果 JSON 记录每篇的来源与校验状态。仍无法获取的文献，请通过所在机构的图书馆/EZproxy 合法获取。

## English
Scripts for downloading academic papers **only from legal open-access sources** (Unpaywall, OpenAlex, arXiv, Semantic Scholar, Europe PMC, NBER, institutional repositories, OSTI). No Sci-Hub. Every PDF is validated with `pdftotext` (title match). Set `UNPAYWALL_EMAIL` env var before running. See table above for each script.
