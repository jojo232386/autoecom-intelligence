"""
Unit tests for QualityChecker.
"""
from engine.cleaner import DataCleaner
from engine.analyzer import DataAnalyzer
from engine.quality_checker import QualityChecker

def test_quality_checker_pass():
    orders, _ = DataCleaner.clean_orders("data/raw_inputs/orders_export.csv")
    ads = DataCleaner.clean_ads("data/raw_inputs/ads_spend_export.csv")
    inv = DataCleaner.clean_inventory("data/raw_inputs/inventory_cost.csv")

    summary = DataAnalyzer.analyze(orders, ads, inv, "测试店铺", "2026-W37")
    audit = QualityChecker.audit(summary)

    assert audit.passed is True
    assert len(audit.errors) == 0
    assert audit.checks["gmv_vs_daily_sum"]["passed"] is True
    assert audit.checks["net_sales_equation"]["passed"] is True
    assert audit.checks["profit_equation"]["passed"] is True

def test_quality_checker_tampered_fails():
    orders, _ = DataCleaner.clean_orders("data/raw_inputs/orders_export.csv")
    ads = DataCleaner.clean_ads("data/raw_inputs/ads_spend_export.csv")
    inv = DataCleaner.clean_inventory("data/raw_inputs/inventory_cost.csv")

    summary = DataAnalyzer.analyze(orders, ads, inv, "测试店铺", "2026-W37")
    # Artificially tamper GMV to simulate hallucination or data corruption
    summary.total_gmv += 1000.0

    audit = QualityChecker.audit(summary)
    assert audit.passed is False
    assert len(audit.errors) > 0
