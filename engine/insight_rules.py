"""
Deterministic business rules and diagnostic engine for e-commerce insights.
Transforms raw metrics into executive-level alerts, quadrant actions, and strategic takeaways.
"""
from typing import List, Tuple
from engine.models import StoreSummary, AnomalyAlert

class InsightEngine:
    @staticmethod
    def generate_diagnostics(summary: StoreSummary) -> Tuple[List[AnomalyAlert], List[str]]:
        anomalies: List[AnomalyAlert] = []
        takeaways: List[str] = []

        # 1. Store-level Health Rules
        if summary.blended_roi < 3.0:
            anomalies.append(AnomalyAlert(
                level="WARNING",
                category="ROI",
                target="全店大盘",
                metric_value=f"{summary.blended_roi}",
                threshold_value=">= 3.50",
                message=f"全店综合投产比 ROI 仅为 {summary.blended_roi}，处于偏低临界线。",
                suggested_action="排查低转化推广计划，削减投产比小于 1.8 的计划预算，提升自然流量权重。"
            ))

        if summary.refund_rate_pct > 15.0:
            anomalies.append(AnomalyAlert(
                level="CRITICAL",
                category="REFUND",
                target="全店大盘",
                metric_value=f"{summary.refund_rate_pct}%",
                threshold_value="<= 12.0%",
                message=f"全店退款率达 {summary.refund_rate_pct}%，侵蚀净利润超过 ¥{summary.total_refunds}。",
                suggested_action="重点审查高退款单品退款原因（尺码不合/色差/质量），加强售前尺码推荐。"
            ))

        # 2. Campaign Level Rules
        for cmp in summary.campaign_metrics:
            if cmp.direct_roi < 1.5 and cmp.total_spend > 2000:
                anomalies.append(AnomalyAlert(
                    level="CRITICAL",
                    category="CAMPAIGN",
                    target=f"{cmp.campaign_name} ({cmp.campaign_id})",
                    metric_value=f"ROI: {cmp.direct_roi}, 消耗: ¥{cmp.total_spend}",
                    threshold_value="ROI >= 2.00",
                    message=f"计划【{cmp.campaign_name}】持续严重亏损，直投产仅 {cmp.direct_roi}，消耗资金 ¥{cmp.total_spend}。",
                    suggested_action="立即压减该计划日预算 50% 或暂停投放，排查定向人群画像与落地页转化率。"
                ))
            elif cmp.direct_roi >= 4.0:
                anomalies.append(AnomalyAlert(
                    level="INFO",
                    category="CAMPAIGN",
                    target=f"{cmp.campaign_name} ({cmp.campaign_id})",
                    metric_value=f"ROI: {cmp.direct_roi}",
                    threshold_value="ROI >= 3.50",
                    message=f"高产出计划【{cmp.campaign_name}】投产比达 {cmp.direct_roi}，处于强红利期。",
                    suggested_action="建议逐步提升 15%-25% 预算，扩大精准人群放量。"
                ))

        # 3. SKU Level Rules
        for s in summary.sku_metrics:
            # Stock urgency on top seller
            if s.current_stock <= s.safety_stock and s.gmv > 10000:
                anomalies.append(AnomalyAlert(
                    level="CRITICAL",
                    category="STOCK",
                    target=f"{s.name} ({s.sku_id})",
                    metric_value=f"库存: {s.current_stock}件",
                    threshold_value=f"安全线: {s.safety_stock}件",
                    message=f"爆款【{s.name}】贡献周GMV ¥{s.gmv}，当前仅剩 {s.current_stock} 件，预计 2-3 天内断货！",
                    suggested_action="立即催促供应链翻单补货，同时适度降低引流控速，避免断货掉权。"
                ))

            # Abnormal refund rate
            if s.refund_rate_pct >= 25.0 and s.orders_count >= 15:
                anomalies.append(AnomalyAlert(
                    level="WARNING",
                    category="REFUND",
                    target=f"{s.name} ({s.sku_id})",
                    metric_value=f"退款率: {s.refund_rate_pct}%",
                    threshold_value="<= 15.0%",
                    message=f"单品【{s.name}】退款率异常飙升至 {s.refund_rate_pct}%（退款额 ¥{s.refund_amount}）。",
                    suggested_action="抽检该批次版型与详情页尺码对照表，排查买家留言高频词并增加试穿视频说明。"
                ))

            # Ad burn / money pit
            if s.quadrant_tag == "吸血亏损":
                anomalies.append(AnomalyAlert(
                    level="CRITICAL",
                    category="ROI",
                    target=f"{s.name} ({s.sku_id})",
                    metric_value=f"推广费 ¥{s.ad_spend}, 投产比 {s.direct_roi}",
                    threshold_value="ROI >= 1.80",
                    message=f"单品【{s.name}】属于典型吸血款，推广费达 ¥{s.ad_spend}，但直产出极低。",
                    suggested_action="暂停该款付费冷启动，转为老客私域测款或关联搭配销售。"
                ))

        # 4. Synthesize Executive Takeaways
        top_sku = summary.sku_metrics[0] if summary.sku_metrics else None
        worst_campaign = next((c for c in summary.campaign_metrics if c.direct_roi < 1.5), None)
        high_refund_sku = next((s for s in summary.sku_metrics if s.refund_rate_pct >= 25.0), None)
        stockout_sku = next((s for s in summary.sku_metrics if s.current_stock <= s.safety_stock and s.gmv > 10000), None)

        takeaways.append(
            f"【大盘概况】本周期全店实现 GMV ¥{summary.total_gmv:,.2f}，净销售额 ¥{summary.total_net_sales:,.2f}，综合毛利率 {summary.gross_profit_margin_pct:.1f}%，综合投产比 Blended ROI 为 {summary.blended_roi:.2f}，经营处于健康盈利状态。"
        )

        if top_sku:
            takeaways.append(
                f"【核心支柱】第一爆款【{top_sku.name}】贡献 GMV ¥{top_sku.gmv:,.2f}（占全店 {(top_sku.gmv/summary.total_gmv*100):.1f}%），毛利贡献稳定。{'⚠️ 需紧急警惕库存仅剩 ' + str(top_sku.current_stock) + ' 件，逼近断货线！' if top_sku.current_stock <= top_sku.safety_stock else '库存周转正常。'}"
            )

        if worst_campaign:
            takeaways.append(
                f"【止血建议】推广计划【{worst_campaign.campaign_name}】持续亏损，花费 ¥{worst_campaign.total_spend:,.2f}，投产比仅 {worst_campaign.direct_roi:.2f}。建议立即压缩日预算 50% 以上，释放资金调优高产出计划。"
            )

        if high_refund_sku:
            takeaways.append(
                f"【品质预警】单品【{high_refund_sku.name}】退款率高达 {high_refund_sku.refund_rate_pct:.1f}%，造成 ¥{high_refund_sku.refund_amount:,.2f} 营业额流失，需立即核查详情页版型参数及买家集中差评。"
            )

        takeaways.append(
            "【下周聚焦】1) 追补第一爆款翻单；2) 砍除低效推广计划，预计下周可提升综合毛利率 3.5-5 个百分点；3) 将潜力爆款转为直通车核心测试组。"
        )

        return anomalies, takeaways
