"""
Business analytics and deterministic calculation engine for e-commerce metrics.
All calculations follow rigorous e-commerce accounting standards.
"""
from collections import defaultdict
from typing import List, Dict, Tuple
from engine.models import (
    CleanedOrder, CleanedAdRecord, InventoryItem,
    DailyMetrics, SKUMetrics, CampaignMetrics, StoreSummary
)

class DataAnalyzer:
    @staticmethod
    def analyze(
        orders: List[CleanedOrder],
        ads: List[CleanedAdRecord],
        inventory: Dict[str, InventoryItem],
        store_name: str = "默认店铺",
        period_label: str = "最近7天经营周报"
    ) -> StoreSummary:
        if not orders:
            return StoreSummary(
                store_name=store_name,
                period_start="",
                period_end="",
                period_label=period_label,
                total_orders=0,
                total_units=0,
                total_gmv=0.0,
                total_refunds=0.0,
                refund_rate_pct=0.0,
                total_net_sales=0.0,
                total_ad_spend=None,
                blended_roi=None,
                total_direct_ad_gmv=None,
                total_cogs=None,
                gross_profit=None,
                gross_profit_margin_pct=None
            )

        # Date range
        order_dates = sorted(list({o.order_date for o in orders}))
        period_start = order_dates[0]
        period_end = order_dates[-1]

        # 1. Total Metrics
        total_orders = len(orders)
        total_units = sum(o.quantity for o in orders)
        total_gmv = round(sum(o.gross_amount for o in orders), 2)
        total_refunds = round(sum(o.refund_amount for o in orders), 2)
        total_net_sales = round(total_gmv - total_refunds, 2)
        refund_rate_pct = round((total_refunds / total_gmv * 100), 2) if total_gmv > 0 else 0.0

        total_ad_spend = round(sum(a.spend for a in ads), 2)
        total_direct_ad_gmv = round(sum(a.direct_gmv for a in ads), 2)
        blended_roi = round(total_gmv / total_ad_spend, 2) if total_ad_spend > 0 else 0.0

        # Refund amount does not establish returned units or recoverable cost.
        def cogs(rows):
            if any(o.sku_id not in inventory or inventory[o.sku_id].cost is None
                   or o.refund_amount > 0 for o in rows):
                return None
            return round(sum(o.quantity * inventory[o.sku_id].cost for o in rows), 2)

        def profit(net, cost, spend):
            return round(net - cost - spend, 2) if cost is not None and ads else None

        def margin(value, net):
            return round(value / net * 100, 2) if value is not None and net > 0 else None

        total_cogs = cogs(orders)
        gross_profit = profit(total_net_sales, total_cogs, total_ad_spend)
        gross_profit_margin_pct = margin(gross_profit, total_net_sales)

        # 2. Daily Metrics
        daily_orders_map = defaultdict(list)
        for o in orders:
            daily_orders_map[o.order_date].append(o)

        daily_ads_map = defaultdict(list)
        for a in ads:
            daily_ads_map[a.date].append(a)

        all_dates = sorted(list(set(order_dates) | set(daily_ads_map.keys())))
        daily_metrics_list: List[DailyMetrics] = []

        for d in all_dates:
            d_orders = daily_orders_map.get(d, [])
            d_ads = daily_ads_map.get(d, [])

            d_count = len(d_orders)
            d_units = sum(o.quantity for o in d_orders)
            d_gmv = round(sum(o.gross_amount for o in d_orders), 2)
            d_refunds = round(sum(o.refund_amount for o in d_orders), 2)
            d_net = round(d_gmv - d_refunds, 2)

            d_spend = round(sum(a.spend for a in d_ads), 2)
            d_direct_gmv = round(sum(a.direct_gmv for a in d_ads), 2)
            d_roi = round(d_gmv / d_spend, 2) if d_spend > 0 else 0.0

            d_cogs = cogs(d_orders)
            d_profit = profit(d_net, d_cogs, d_spend)
            d_margin = margin(d_profit, d_net)

            daily_metrics_list.append(DailyMetrics(
                date=d,
                orders_count=d_count,
                units_sold=d_units,
                gmv=d_gmv,
                refunds=d_refunds,
                net_sales=d_net,
                ad_spend=d_spend if ads else None,
                direct_ad_gmv=d_direct_gmv if ads else None,
                blended_roi=d_roi if d_spend > 0 else None,
                gross_profit=d_profit,
                profit_margin_pct=d_margin
            ))

        # 3. SKU Metrics
        sku_orders_map = defaultdict(list)
        for o in orders:
            sku_orders_map[o.sku_id].append(o)

        sku_ads_map = defaultdict(list)
        for a in ads:
            sku_ads_map[a.target_sku].append(a)

        all_skus = sorted(list(set(inventory.keys()) | set(sku_orders_map.keys())))
        sku_metrics_list: List[SKUMetrics] = []

        for s_id in all_skus:
            s_orders = sku_orders_map.get(s_id, [])
            s_ads = sku_ads_map.get(s_id, [])
            inv_item = inventory.get(s_id)

            sku_name = inv_item.name if inv_item else (s_orders[0].sku_name if s_orders else s_id)
            category = inv_item.category if inv_item else (s_orders[0].category if s_orders else "未分类")
            current_stock = inv_item.stock if inv_item else None
            safety_stock = inv_item.safety_stock if inv_item else None
            unit_cost = inv_item.cost if inv_item else None

            s_count = len(s_orders)
            s_units = sum(o.quantity for o in s_orders)
            s_gmv = round(sum(o.gross_amount for o in s_orders), 2)
            s_refund = round(sum(o.refund_amount for o in s_orders), 2)
            s_net = round(s_gmv - s_refund, 2)
            s_refund_pct = round((s_refund / s_gmv * 100), 2) if s_gmv > 0 else 0.0

            s_ad_spend = round(sum(a.spend for a in s_ads), 2)
            s_direct_gmv = round(sum(a.direct_gmv for a in s_ads), 2)
            s_direct_roi = round(s_direct_gmv / s_ad_spend, 2) if s_ad_spend > 0 else 0.0

            s_cogs = cogs(s_orders)
            s_profit = profit(s_net, s_cogs, s_ad_spend)
            s_margin_pct = margin(s_profit, s_net)

            # Stock turnover status
            if current_stock is not None and safety_stock is not None and current_stock <= safety_stock:
                stock_status = "缺货告急"
            elif current_stock is not None and safety_stock is not None and current_stock > safety_stock * 8:
                stock_status = "库存积压"
            else:
                stock_status = "未提供" if current_stock is None or safety_stock is None else "周转健康"

            # Quadrant tagging & alerts
            alerts = []
            if current_stock is not None and safety_stock is not None and current_stock <= safety_stock:
                alerts.append(f"库存告急: 仅剩{current_stock}件 (警戒线{safety_stock})")
            if s_refund_pct >= 20.0:
                alerts.append(f"高退款率预警: {s_refund_pct}%")
            if s_ad_spend > 1500 and s_direct_roi < 1.5:
                alerts.append(f"高消耗低投产预警: 花费¥{s_ad_spend}, ROI仅{s_direct_roi}")

            if s_ad_spend > 1500 and s_direct_roi < 1.6:
                quadrant = "吸血亏损"
            elif s_refund_pct >= 22.0:
                quadrant = "退款隐患"
            elif s_gmv >= (total_gmv * 0.18) and s_refund_pct <= 15.0:
                quadrant = "现金金牛"
            elif s_direct_roi >= 2.0 or (s_margin_pct is not None and s_margin_pct >= 25.0 and s_gmv >= 5000):
                quadrant = "潜力爆品"
            else:
                quadrant = "平销防守"

            quadrant = "数据不足，暂停利润结论" if s_profit is None else ("贡献利润为负" if s_profit < 0 else "贡献利润非负")

            sku_metrics_list.append(SKUMetrics(
                sku_id=s_id,
                name=sku_name,
                category=category,
                orders_count=s_count,
                units_sold=s_units,
                gmv=s_gmv,
                refund_amount=s_refund,
                net_sales=s_net,
                refund_rate_pct=s_refund_pct,
                ad_spend=s_ad_spend if ads else None,
                direct_ad_gmv=s_direct_gmv if ads else None,
                direct_roi=s_direct_roi if s_ad_spend > 0 else None,
                estimated_cogs=s_cogs,
                gross_profit=s_profit,
                gross_margin_pct=s_margin_pct,
                current_stock=current_stock,
                safety_stock=safety_stock,
                stock_turnover_status=stock_status,
                quadrant_tag=quadrant,
                alert_flags=alerts
            ))

        # Sort SKUs by GMV descending
        sku_metrics_list.sort(key=lambda x: x.gmv, reverse=True)

        # 4. Campaign Metrics
        campaign_map = defaultdict(list)
        for a in ads:
            campaign_map[a.campaign_id].append(a)

        campaign_metrics_list: List[CampaignMetrics] = []
        for c_id, c_records in campaign_map.items():
            c_name = c_records[0].campaign_name
            c_target = c_records[0].target_sku
            c_spend = round(sum(r.spend for r in c_records), 2)
            c_imp = sum(r.impressions for r in c_records)
            c_clicks = sum(r.clicks for r in c_records)
            c_direct_gmv = round(sum(r.direct_gmv for r in c_records), 2)
            c_cpc = round(c_spend / c_clicks, 2) if c_clicks > 0 else 0.0
            c_ctr = round(c_clicks / c_imp * 100, 2) if c_imp > 0 else 0.0
            c_roi = round(c_direct_gmv / c_spend, 2) if c_spend > 0 else 0.0

            if c_roi >= 3.0:
                tag = "高效放量"
            elif c_roi >= 2.0:
                tag = "维持观察"
            else:
                tag = "控比压减"

            campaign_metrics_list.append(CampaignMetrics(
                campaign_id=c_id,
                campaign_name=c_name,
                target_sku=c_target,
                total_spend=c_spend,
                impressions=c_imp,
                clicks=c_clicks,
                overall_cpc=c_cpc,
                overall_ctr_pct=c_ctr,
                direct_gmv=c_direct_gmv,
                direct_roi=c_roi,
                status_tag=tag
            ))

        campaign_metrics_list.sort(key=lambda x: x.total_spend, reverse=True)

        return StoreSummary(
            store_name=store_name,
            period_start=period_start,
            period_end=period_end,
            period_label=period_label,
            total_orders=total_orders,
            total_units=total_units,
            total_gmv=total_gmv,
            total_refunds=total_refunds,
            refund_rate_pct=refund_rate_pct,
            total_net_sales=total_net_sales,
            total_ad_spend=total_ad_spend if ads else None,
            blended_roi=blended_roi if total_ad_spend > 0 else None,
            total_direct_ad_gmv=total_direct_ad_gmv if ads else None,
            total_cogs=total_cogs,
            gross_profit=gross_profit,
            gross_profit_margin_pct=gross_profit_margin_pct,
            daily_metrics=daily_metrics_list,
            sku_metrics=sku_metrics_list,
            campaign_metrics=campaign_metrics_list
        )
