# 「极简周报」电商代运营多店铺经营分析与白牌周报自动化引擎
> **AutoEcom Analytics White-label Delivery Engine**  
> 一套低人工参与、纯确定性核算、闭环自检、高溢价白牌代工的 AI 自动化商业交付系统。
> 
> 🌐 **公网作品页**: [jojo232386.github.io/autoecom-intelligence](https://jojo232386.github.io/autoecom-intelligence/)  
> 📊 **全屏交互看板实时 Demo**: [在线体验 Interactive Dashboard](https://jojo232386.github.io/autoecom-intelligence/demo.html)  
> 🚀 **免费申领单店试跑 (Free Pilot)**: [立即在 GitHub 提交试单工单](https://github.com/jojo232386/autoecom-intelligence/issues/new?template=01_request_free_pilot.yml)  
> 🏛️ **代运营机构白牌包月合作**: [提交代工咨询](https://github.com/jojo232386/autoecom-intelligence/issues/new?template=02_agency_whitelabel_inquiry.yml)

---

## 🚀 业务定位与价值公式

- **服务对象**：电商代运营公司 (TP / DP)、矩阵式店铺操盘工作室、中小品牌电商团队。
- **痛点替代**：替代运营助理每周一花费 10~20 小时手动导表、VLOOKUP 拼凑、PPT 制图的机械苦力。
- **核心承诺**：
  - **交付速度**：从人工 2 天缩短至 **系统 3 秒**。
  - **核算精度**：**100% 会计级勾稽关系核验**，杜绝大模型数字幻觉与人工抄写错误。
  - **白牌赋能**：100% 白牌交付，代运营打上自己的 Logo 交付甲方品牌，提高代运营续费率与溢价。
  - **投入产出比**：代工成本仅为雇佣专职数据助理的 1/5。

---

## 📦 标准化交付成果 (4合1交付包)

执行系统后，将在 `data/deliverables/` 自动生成全套可直接交付客户的成果：

| 交付成果 | 文件格式 | 核心价值 |
| :--- | :--- | :--- |
| **全屏交互式看板** | `weekly_dashboard.html` | 现代化 Dark/Light 响应式看板，含 KPI 卡片、日度走势图、SKU 四象限矩阵、计划投产诊断。支持浏览器打开按 `Cmd+P` 一键导出高端 PDF。 |
| **多Sheet审计级报表** | `weekly_report.xlsx` | 包含 5 大 Sheet：`经营周报总览_KPI`、`每日明细对账_Daily`、`SKU经营透视_Products`、`投流计划ROI_Ads`、`质检与勾稽平衡表_Audit`。自动格式化货币、百分比与斑马纹。 |
| **高管速递摘要** | `executive_briefing.md` | 60 秒极简提炼，包含大盘战绩、第一爆款断货预警、亏损计划止血建议、下周运营聚焦。可直接复制发送微信群或飞书。 |
| **物理勾稽核验单** | `quality_audit_report.json` | 机器可读的核验凭据，记录 GMV 平衡、净销平衡、SKU 汇总、广告消耗勾稽差异（diff=0.0）。 |

---

## 🛠️ 快速上手与运行指令

### 1. 激活环境
```bash
cd /Users/ASUS/Desktop/agy3
source .venv/bin/activate
```

### 2. 一键全流程执行
```bash
# 使用默认样例数据直接生成
python cli.py

# 指定自定义店铺与输入文件
python cli.py \
  --orders data/raw_inputs/orders_export.csv \
  --ads data/raw_inputs/ads_spend_export.csv \
  --inventory data/raw_inputs/inventory_cost.csv \
  --store "美澜风尚旗舰店" \
  --period "2026-W37周报" \
  --agency "星瀚数字代运营" \
  --out data/deliverables
```

### 3. 运行自动化测试套件
```bash
pytest
```
*(全部 8 项测试涵盖清洗层、计算层、象限分类、勾稽核验与集成管线，100% Green)*

---

## 📁 目录结构

```
/Users/ASUS/Desktop/agy3/
├── business/                               # 商业化运营与拓客闭环
│   ├── 01_market_research_top3.md         # Top 3 落地场景深度调研与评分
│   ├── 02_commercial_offer.md             # 最小可售产品规格、定价阶梯与服务边界
│   ├── 03_client_prospects_and_channels.md # 5大渠道客户画像与杠杆渠道库
│   └── 04_cold_outreach_templates.md      # 微信私聊/渠道分成/社群引流实战话术
├── engine/                                 # 核心自动化引擎
│   ├── models.py                          # 领域数据模型
│   ├── cleaner.py                         # 跨平台表头模糊对齐与脏数据清洗
│   ├── analyzer.py                        # 确定性会计指标与SKU象限分析
│   ├── insight_rules.py                   # 业务诊断规则库与行动建议引擎
│   ├── quality_checker.py                 # 会计级物理勾稽自检
│   ├── report_generator.py                # HTML看板、Excel工作簿与摘要生成器
│   └── pipeline.py                        # 全流程自动化集成调度
├── data/
│   ├── raw_inputs/                        # 真实多平台导出样例 (含异常边缘场景)
│   └── deliverables/                      # 自动生成的全套交付成果
├── tests/                                 # 自动化测试套件
├── scripts/                               # 数据仿真与测试脚本
├── cli.py                                 # 命令行启动入口
└── README.md                              # 业务与系统总览
```

---

## 💰 商业变现行动路线图 (Action Plan)

1. **第一阶段：以测促单（本周）**
   - 目标：获取首个真实付费客户。
   - 策略：使用 `business/04_cold_outreach_templates.md` 中的【模版一】，向 20-30 家中小型代运营公司/工作室负责人发送私信，提供**【免费试测 1 家店铺周报】**。
   - 转化：交付后展现惊艳的 HTML 看板与 Excel，提供 ¥99 尝鲜价或 ¥1,999/月 白牌包月。
2. **第二阶段：渠道杠杆（第 2~4 周）**
   - 目标：签约 2~3 家代运营服务商，锁定 15~30 家店铺，稳定月流水 ¥4,500 ~ ¥10,000。
   - 策略：主攻代运营机构白牌代工，帮其团队直接减负。
3. **第三阶段：无人化全自动托管**
   - 目标：人工参与度降至 5% 以下。
   - 策略：配置网盘/微信群机器人自动接收客户扔进来的 CSV/Excel，定时触发 `python cli.py`，质检通过后自动回传成果，仅在质检报警时人工介入。
