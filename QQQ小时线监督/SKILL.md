---
name: qqq-hourly-audit
description: 用独立复算加 Gemini 第三方审核，监督 QQQ 小时线抄底模型（自主学习 bot），重点查幻觉、编造数据、前视偏差、数据泄漏和虚假文献。
---
# QQQ小时线监督：第三方审核流程

## 用途
独立审核"自主学习"bot 在 /workspace/qqq_hourly_rl/ 中的 QQQ 小时线模型工作。我审核通过之前，它不得把结果报为最终结论。

## 触发场景
- 自主学习发来五项格式的审核清单：改动、代码、结果、关键数字、文献。
- 自主学习报告整改完成，请求复核。

## 步骤
1. 读代码和结果文件，逐条核对它说的改动是否真的存在，并给出"文件:行号"作为证据。
2. 用独立脚本复算它报告的数字。不额外查看验证集：已登记的查看次数（OOS_LOG.md）只能增加；如果复算本身会构成一次查看，就跳过并在报告中写明。
3. 测试脚本放在副本目录（/tmp）里运行，前后比对正式文件的 sha256；至少做一次变异测试，确认断言确实能失败。
4. 前推检查：确认数据含完整收盘（美东 16:00），没有用到不完整 K 线或未来数据，信号时点和成交假设一致。
5. 用 gemini_chat/gemini_chat.py 接着原有的历史让 Gemini 审核。
6. 用代码逐条核实 Gemini 的说法。Gemini 每轮都有误报，常见的是夸大、编造代码细节、判得太宽。核实结论作为一条 user 消息追加进历史。
7. 写报告 audit_*_verification.md，结论分为：通过 / 有条件通过 / 不通过。
8. 把整改清单发给自主学习；重要结论用中文告诉 Taz。

## 数据源与工具
- 代码和数据：/workspace/qqq_hourly_rl/，/workspace/data（环境变量 QDATA），日线 VIX（环境变量 QVIXD）。
- Gemini API：generativelanguage.googleapis.com v1beta generateContent，key 在环境变量 GEMINI_API_KEY 中。默认模型 gemini-3.8-flash，遇到 429 或 503 时换 gemini-3-flash-preview。
- 持续对话：gemini_chat/history.json（contents 格式）和 system_instruction.txt。支持 --cache（cachedContents 缓存）和 --compress N（把旧轮压缩成摘要，但保留已确认的结论）。
- 参考：/workspace/final_indicators_list.md（基础指标清单，发明者和年份大多未核实）。

## 原则
只认代码和数据；不确定就标"未核实"；不编造数字；所有交流都用中文。
