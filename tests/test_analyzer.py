"""
Unit tests for DataAnalyzer.
"""
from engine.cleaner import DataCleaner
from engine.analyzer import DataAnalyzer

def test_data_analyzer_metrics():
    orders, _ = DataCleaner.clean_orders("tests/fixtures/orders_export.csv")
    ads = DataCleaner.clean_ads("tests/fixtures/ads_spend_export.csv")
    inv = DataCleaner.clean_inventory("tests/fixtures/inventory_cost.csv")

    summary = DataAnalyzer.analyze(orders, ads, inv, "测试店铺", "2026-W37")

    assert summary.total_orders == len(orders)
    assert summary.total_gmv > 0
    assert summary.total_net_sales == round(summary.total_gmv - summary.total_refunds, 2)
    assert summary.blended_roi > 0
    assert summary.gross_profit is None  # Refund recovery rules absent
    assert len(summary.daily_metrics) == 7
    assert len(summary.sku_metrics) == 10
    assert len(summary.campaign_metrics) == 5

    # Check top SKU
    top_sku = summary.sku_metrics[0]
    assert top_sku.gmv > 0
    assert top_sku.units_sold > 0
    assert top_sku.quadrant_tag in ["数据不足，暂停利润结论"]
