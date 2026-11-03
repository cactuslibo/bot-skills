# QQQ小时线监督 · 代码说明

- `gemini_chat.py`：与 Gemini 进行多轮审计对话的命令行工具，支持历史记录、cachedContents 缓存旧历史、历史压缩等。
- `build_history.py`：从本地审计材料（Markdown 文件）重建 Gemini 对话历史 `history.json`。其中的路径 `/workspace/qqq_hourly_rl` 是作者本机目录，使用时请改成自己的路径。

API key 从环境变量 `GEMINI_API_KEY` 读取，代码中不含任何 key：

```bash
export GEMINI_API_KEY=你的key
```

注：history.json、system_instruction.txt、缓存状态与数据文件均未上传。
