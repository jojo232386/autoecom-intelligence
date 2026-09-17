# 客户回复破冰、异议处理与锁单话术库（Objection Handling & Closing SOP）

当陌生客户在 Upwork、猪八戒或微信回复你时，**前 3 次互动的质量决定了 80% 的成单率**。

---

## 场景一：客户回复并提供了他的真实表格（成交黄金时刻）

### 客户说：
> "Hi, I have attached my raw export. Can your script process this?"
> 或 "这是我们店导出来的几张表，你能做成你发的那种看板吗？"

### 你的应对动作（让 Agent 跑，你复制文案）：
1. **你把客户发来的表格保存到 `data/raw_inputs/` 目录**。
2. **让 Agent 执行管线**：`python cli.py --orders <客户表> --store <客户店铺名>`。
3. **把生成的 HTML 看板和 Excel 截图/打包直接回传给客户**。
4. **回复文案**：
   - **英文客户**：
     > *"Hi [Client Name], I have already processed your sample file. Here is the generated interactive HTML dashboard and formatted Excel workbook for your review [Attached]. All checksums matched with 0.0 variance. If this looks good to you, you can activate the milestone on Upwork and I will hand over the final source code and setup instructions immediately!"*
   - **中文客户**：
     > *"XX总，我已经用您的样本跑出了一版完整周报看板和多Sheet表格（见附件/截图）。所有数据已经通过日度与SKU勾稽核验。您看一下这个格式和诊断维度是否符合您的预期？如果没问题，咱们可以正式确认订单，我把整套自动化配置交付给您！"*

---

## 场景二：客户质疑价格（"别人报价只要 $30，你为什么报 $100？"）

### 破局核心：
不要降价迎合低端竞争。强调**“免维护稳定性”与“会计级零差错”**。

### 回复话术：
> **英文**：
> *"I completely understand! The difference is in engineering robustness: A \$30 quick script usually hardcodes column indices and breaks the moment your platform changes a header or outputs a date with a slash. It also doesn't perform double-entry reconciliation, which leads to silent formula errors in front of your clients. 
> 
> My engine includes fuzzy header matching, multi-format sanitization, and an automated audit trail (diff=0.0 check). You get a production-grade asset that works unattended every week, not a fragile one-off script."*
> 
> **中文**：
> *"理解您的考虑！市面上几十块钱的兼职脚本通常是写死列坐标的，平台一旦改个表头或者日期多带个空格，下周就直接报错瘫痪；更严重的是没有对账核验，很容易向老板或甲方报出错误的ROI。
> 
> 我们交付的是工业级的数据管线：自动纠错脏数据、支持异常报警、自带会计级勾稽核验，确保每周一自动运行不出纰漏。省下的排查时间远超差价。"*

---

## 场景三：客户要求“先做完看看，再付款”

### 回复话术：
> **英文**：
> *"I am so confident in the delivery that I will happily process your first 20 rows and show you the exact HTML preview for free. Once you verify that the preview is 100% accurate, we can fund the milestone on Upwork before I deliver the full dataset and code. That way, your risk is absolute zero."*
> 
> **中文**：
> *"完全没问题！为消除您的顾虑，您可以随便发我 10~20 行脱敏数据，我免费帮您跑出一份预览看板。您确认效果和计算完全无误后，咱们再在平台走正常担保交易交付全量。"*
