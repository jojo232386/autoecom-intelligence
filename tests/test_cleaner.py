"""
Unit tests for DataCleaner.
"""
import pytest
from engine.cleaner import clean_currency_str, parse_date_str, map_headers, DataCleaner, HEADER_ALIASES

def test_clean_currency_str():
    assert clean_currency_str(" ¥289.00 ") == 289.0
    assert clean_currency_str("￥1,250.50") == 1250.5
    assert clean_currency_str("$99.9") == 99.9
    assert clean_currency_str(100) == 100.0
    assert clean_currency_str(None) == 0.0
    assert clean_currency_str("invalid") == 0.0

def test_parse_date_str():
    d1, dt1 = parse_date_str("2026-09-08 15:30:00")
    assert d1 == "2026-09-08"
    assert dt1 == "2026-09-08 15:30:00"

    d2, dt2 = parse_date_str("2026/09/09 18:20:10")
    assert d2 == "2026-09-09"
    assert dt2 == "2026-09-09 18:20:10"

    d3, _ = parse_date_str("2026-09-10")
    assert d3 == "2026-09-10"

def test_map_headers():
    headers = ["子订单编号", "下单时间", "商品编码", "买家实付金额", "订单当前状态"]
    mapped = map_headers(headers, HEADER_ALIASES)
    assert mapped["order_id"] == "子订单编号"
    assert mapped["order_time"] == "下单时间"
    assert mapped["sku_id"] == "商品编码"
    assert mapped["gross_amount"] == "买家实付金额"
    assert mapped["order_status"] == "订单当前状态"

def test_clean_orders_file():
    orders, stats = DataCleaner.clean_orders("tests/fixtures/orders_export.csv")
    assert stats["total_rows"] > 0
    assert stats["paid_orders"] > 0
    assert stats["filtered_unpaid"] > 0
    assert len(orders) == stats["paid_orders"]
    for o in orders:
        assert o.gross_amount > 0
        assert o.quantity >= 1
        assert o.is_valid_paid is True
