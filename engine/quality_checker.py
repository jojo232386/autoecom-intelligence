"""
Closed-loop accounting verification and mathematical audit engine.
Enforces double-entry style consistency checks to eliminate numerical hallucinations and errors.
"""
from datetime import datetime
from typing import Dict, Any, List
from engine.models import StoreSummary, AuditResult

class QualityChecker:
    @staticmethod
    def audit(summary: StoreSummary) -> AuditResult:
        checks: Dict[str, Any] = {}
        warnings: List[str] = []
        errors: List[str] = []

        # 1. Checksum: Total GMV vs Daily Sum
        daily_gmv_sum = round(sum(d.gmv for d in summary.daily_metrics), 2)
        diff_daily_gmv = round(abs(summary.total_gmv - daily_gmv_sum), 2)
        check_1 = diff_daily_gmv < 0.02
        checks["gmv_vs_daily_sum"] = {
            "total_gmv": summary.total_gmv,
            "daily_sum": daily_gmv_sum,
            "diff": diff_daily_gmv,
            "passed": check_1
        }
        if not check_1:
            errors.append(f"GMV勾稽校验失败: 总GMV({summary.total_gmv}) != 每日汇总({daily_gmv_sum}), 差异={diff_daily_gmv}")

        # 2. Checksum: Net Sales Balance Equation
        calculated_net = round(summary.total_gmv - summary.total_refunds, 2)
        diff_net = round(abs(summary.total_net_sales - calculated_net), 2)
        check_2 = diff_net < 0.02
        checks["net_sales_equation"] = {
            "total_net_sales": summary.total_net_sales,
            "calculated_net": calculated_net,
            "diff": diff_net,
            "passed": check_2
        }
        if not check_2:
            errors.append(f"净销售额勾稽校验失败: 净销售({summary.total_net_sales}) != GMV-退款({calculated_net})")

        # 3. Checksum: Total GMV vs SKU Sum
        sku_gmv_sum = round(sum(s.gmv for s in summary.sku_metrics), 2)
        diff_sku_gmv = round(abs(summary.total_gmv - sku_gmv_sum), 2)
        check_3 = diff_sku_gmv < 0.02
        checks["gmv_vs_sku_sum"] = {
            "total_gmv": summary.total_gmv,
            "sku_sum": sku_gmv_sum,
            "diff": diff_sku_gmv,
            "passed": check_3
        }
        if not check_3:
            errors.append(f"SKU汇总勾稽校验失败: 总GMV({summary.total_gmv}) != SKU汇总({sku_gmv_sum})")

        # 4. Checksum: Total Ad Spend vs Campaign Sum
        campaign_spend_sum = round(sum(c.total_spend for c in summary.campaign_metrics), 2)
        diff_spend = round(abs(summary.total_ad_spend - campaign_spend_sum), 2)
        check_4 = diff_spend < 0.02
        checks["ad_spend_vs_campaign_sum"] = {
            "total_ad_spend": summary.total_ad_spend,
            "campaign_spend_sum": campaign_spend_sum,
            "diff": diff_spend,
            "passed": check_4
        }
        if not check_4:
            errors.append(f"推广花费勾稽校验失败: 总消耗({summary.total_ad_spend}) != 计划汇总({campaign_spend_sum})")

        # 5. Checksum: Profit Equation Balance
        expected_profit = round(summary.total_net_sales - summary.total_cogs - summary.total_ad_spend, 2)
        diff_profit = round(abs(summary.gross_profit - expected_profit), 2)
        check_5 = diff_profit < 0.02
        checks["profit_equation"] = {
            "gross_profit": summary.gross_profit,
            "expected_profit": expected_profit,
            "diff": diff_profit,
            "passed": check_5
        }
        if not check_5:
            errors.append(f"毛利勾稽校验失败: 毛利润({summary.gross_profit}) != 净销-成本-广告({expected_profit})")

        # 6. Non-negativity & Data Sanity
        if summary.total_orders <= 0:
            errors.append("有效支付订单数为 0")
        if summary.total_gmv < 0:
            errors.append("总 GMV 为负数")
        if summary.total_refunds < 0:
            errors.append("退款总额为负数")
        if summary.total_ad_spend < 0:
            errors.append("推广消耗为负数")

        passed = len(errors) == 0

        return AuditResult(
            passed=passed,
            checks=checks,
            warnings=warnings,
            errors=errors,
            checked_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
