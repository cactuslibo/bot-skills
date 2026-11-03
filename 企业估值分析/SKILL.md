---
name: 企业估值分析
description: 对上市公司做企业估值与产业链/商业模式分析（DCF、可比公司、反向DCF、SOTP、情景估值、毛利率驱动拆解），全程中文。
---

# 企业估值分析

## 用途
为 Taz 估算上市公司合理价值、判断高估/低估，并拆解其上下游与盈利驱动因素。

## 触发场景
- “X 值多少钱 / 合理价 / 高估还是低估”
- “分析 X 的上下游 / 产业链”
- 情景估值（如 AI 制药繁荣情景）、反向 DCF 看市场隐含预期
- “为什么某业务毛利率这么高”等商业模式问题

## 步骤
1. 确认标的与代码（有歧义先问，如 tem → Tempus AI/TEM）。
2. 取数：SEC EDGAR（10-K/10-Q、XBRL）、yfinance 行情与财务、公司投资者材料；每个数字记来源与日期，禁止编造。
3. 估值三角验证：
   - DCF（FCFF，WACC、beta、终值，敏感性表）
   - 可比公司倍数（EV/Sales、EV/EBITDA、P/E）
   - 反向 DCF（当前股价隐含增长/利润率）
   - 需要时：SOTP、DDM、三情景（熊/基/牛，可加约束/无约束版本）
   - 全面摊薄股本（含可转债）
4. 给出区间与中枢，对比现价，说明关键假设与风险。
5. 多 bot 协作：产业研究（行业/竞争）、网络信息搜索（新闻与披露）、文献搜索+SciHub（学术证据），汇总交叉验证后中文交付。
6. 产出写入 /workspace/<标的>_analysis/*.md，模型脚本（model.py）可复用。

## 工具与数据源
- 已安装估值技能：valuation-dcf/comps/lbo/three-statement/merger/returns-anthropic、valuation-company-himself65、valuation-dcf-governed-noahnan、valuation-damodaran-analystcollective、valuation-reverse-dcf/ddm/sotp/methods-agentii
- 依赖：/workspace/valuation_skills/repos/ 与 /workspace/valuation_skills/venv
- 数据：SEC EDGAR、yfinance（均免费）；付费 key 须先问 Taz

## 原则
- 全程中文；数字必须有来源；结论给区间不给单点；区分事实与推论。
