---
name: 市场规模
description: 当需要测算某个市场当前有多大（TAM/SAM/SOM）、预测成长市场的未来规模（渗透率 S 曲线、Bass 扩散、学习曲线、牛/基/熊情景），或者测算药品、适应症的市场规模（患者漏斗）时使用。
---

# 市场规模分析

## 用途
- 测算当前市场规模，比如某类玩具或某种癌症药物的市场。
- 预测潜在成长市场，比如新能源车、低空飞行器。

## 通用铁律
- 自上而下和自下而上两种方法都要做，并且要互相对账；两者相差超过 50% 时必须写出原因。
- 每个输入都要写明来源、日期和 URL，并标注它属于“来源”“推导”还是“假设”。
- 结果只给区间，禁止编造数字；找不到的数据写“未找到/数据缺口”。

## 工作流 1：当前市场测算（skill：market-sizing-current）
1. 先给市场下定义：产品、客户、渠道、地理、年份、单位、价格口径，并列出包含和不包含的范围。
2. 自上而下：行业总额 × 品类占比 × 地区占比 × 渠道占比 × 价格带占比。
3. 自下而上：按业务类型选公式，比如门店数 × 铺货率 × 动销 × 净价，或目标人群 × 使用率 × 频次 × 客单价，或机构数 × 采购率 × 单机构支出，或供给法。
4. 对账、做敏感性分析，再按 TAM → SAM → SOM 的顺序依次收窄。

## 工作流 2：成长市场预测（skill：market-forecast-growth）
1. 先定预测契约，也就是哪些指标、由哪个数据方结算；再取基准值和 nowcast。
2. 历史基准率：找成功类比和停滞类比，看它们从 1% 到 10% 再到 50% 渗透各用了多久。
3. 驱动恒等式：存量和流量分开算；把采用门槛链拆清楚。
4. 模型：Logistic S 曲线 P(t)=K/(1+e^(−r(t−t0)))；Bass 扩散模型（m、p、q）；学习曲线 C(x)=floor+(C0−floor)(x/x0)^(−b)。拟合用 bass_fit.py 脚本。
5. 检查供给是否跟得上；设牛/基/熊情景并给出权重（政策目标不能当中心预测）；最后列出用来证伪的路标。

## 工作流 3：医药市场（skill：pharma-market-sizing）
1. 患者漏斗依次相乘：患病率或发病率 → 诊断率 → 治疗率 → 符合标签的可及份额 → 峰值份额 → 依从率或疗程 → 年治疗费（净价）。
2. 慢病要做停药调整；上市后按 S 型爬坡；生物药和细胞基因治疗要检查产能。
3. 用同类药实际销售额做自上而下对账；最后给出牛/基/熊情景和敏感性分析。

## 数据源（免费）
- 中国：国家统计局、海关总署、工信部、中汽协、乘联会、巨潮资讯、国家医保局、国家癌症中心。
- 美国：Census、BLS、BEA、SEC EDGAR、CMS、SEER、CDC WONDER。
- 国际：World Bank API、OECD、DBnomics、UN Comtrade、IEA、IRENA、Our World in Data、GLOBOCAN、PubMed、ClinicalTrials.gov。
- 付费数据源（IQVIA、Euromonitor 等）只在用户提供时使用。

## 方法来源
latour-ai/skills market-sizing-builder；AlphaMao1/AlphaMao_Skills market-sizing；atypica-ai/marketing-skills market-sizing；deanpeters/Product-Manager-Skills tam-sam-som-calculator；linroger/DeepResearchForecast industry-forecasting；asgard-ai-platform grad-innovation-diffusion-bass；rsingla92/scientificduediligence market；agentii med-market-sizing（只借鉴方法）。
