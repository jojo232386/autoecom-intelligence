"""
End-to-End Orchestrator Pipeline for E-commerce Intelligence Delivery.
Connects Cleaner -> Analyzer -> Insights -> Quality Check -> Deliverable Generation.
"""
import os
import json
from typing import Dict, Any, Optional
from engine.cleaner import DataCleaner
from engine.analyzer import DataAnalyzer
from engine.insight_rules import InsightEngine
from engine.quality_checker import QualityChecker
from engine.report_generator import ReportGenerator

class IntelligencePipeline:
    def __init__(
        self,
        orders_path: str,
        ads_path: Optional[str] = None,
        inventory_path: Optional[str] = None,
        store_name: str = "美澜风尚旗舰店",
        period_label: str = "2026-W37周报",
        agency_name: str = "代运营白牌数字化中心",
        output_dir: str = "data/deliverables"
    ):
        self.orders_path = orders_path
        self.ads_path = ads_path
        self.inventory_path = inventory_path
        self.store_name = store_name
        self.period_label = period_label
        self.agency_name = agency_name
        self.output_dir = output_dir

    def run(self, fail_on_audit: bool = True) -> Dict[str, Any]:
        os.makedirs(self.output_dir, exist_ok=True)

        # 1. Clean Inputs
        if not os.path.exists(self.orders_path):
            raise FileNotFoundError(f"订单文件未找到: {self.orders_path}")
        
        orders, order_stats = DataCleaner.clean_orders(self.orders_path)
        
        for optional_path in (self.ads_path, self.inventory_path):
            if optional_path and not os.path.isfile(optional_path):
                raise FileNotFoundError("Provided input missing")
        ads = []
        if self.ads_path and os.path.exists(self.ads_path):
            ads = DataCleaner.clean_ads(self.ads_path)
            
        inventory = {}
        if self.inventory_path and os.path.exists(self.inventory_path):
            inventory = DataCleaner.clean_inventory(self.inventory_path)

        # 2. Analyze
        summary = DataAnalyzer.analyze(
            orders=orders,
            ads=ads,
            inventory=inventory,
            store_name=self.store_name,
            period_label=self.period_label
        )

        # 3. Insights
        anomalies, takeaways = InsightEngine.generate_diagnostics(summary)
        summary.anomalies = anomalies
        summary.executive_takeaways = takeaways

        # 4. Quality Audit
        audit = QualityChecker.audit(summary)
        if fail_on_audit and not audit.passed:
            raise ValueError(f"质量勾稽审计未通过: {'; '.join(audit.errors)}")

        # 5. Generate Deliverables
        html_file = os.path.join(self.output_dir, "weekly_dashboard.html")
        xlsx_file = os.path.join(self.output_dir, "weekly_report.xlsx")
        brief_file = os.path.join(self.output_dir, "executive_briefing.md")
        audit_file = os.path.join(self.output_dir, "quality_audit_report.json")

        ReportGenerator.generate_html_dashboard(summary, audit, html_file, self.agency_name)
        ReportGenerator.generate_excel_workbook(summary, audit, xlsx_file, self.agency_name)
        ReportGenerator.generate_executive_briefing(summary, audit, brief_file, self.agency_name)

        audit_data = {
            "passed": audit.passed,
            "checked_at": audit.checked_at,
            "checks": audit.checks,
            "errors": audit.errors,
            "warnings": audit.warnings,
            "store_summary_snapshot": {
                "store_name": summary.store_name,
                "period_label": summary.period_label,
                "total_orders": summary.total_orders,
                "total_units": summary.total_units,
                "total_gmv": summary.total_gmv,
                "total_net_sales": summary.total_net_sales,
                "total_refunds": summary.total_refunds,
                "refund_rate_pct": summary.refund_rate_pct,
                "total_ad_spend": summary.total_ad_spend,
                "blended_roi": summary.blended_roi,
                "gross_profit": summary.gross_profit,
                "gross_profit_margin_pct": summary.gross_profit_margin_pct
            }
        }
        with open(audit_file, "w", encoding="utf-8") as f:
            json.dump(audit_data, f, ensure_ascii=False, indent=2)

        return {
            "status": "SUCCESS",
            "audit_passed": audit.passed,
            "deliverables": {
                "html_dashboard": html_file,
                "excel_workbook": xlsx_file,
                "executive_briefing": brief_file,
                "audit_report": audit_file
            },
            "summary": audit_data["store_summary_snapshot"],
            "cleaning_stats": order_stats
        }
