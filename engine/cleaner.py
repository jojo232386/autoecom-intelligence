"""
Data cleaning and normalization engine for multi-platform e-commerce exports.
Features:
- Fuzzy header alignment across Taobao, Douyin, PDD, JD, and ERP formats
- Dirty string/currency parsing (strips whitespace, symbols, commas)
- Date format unification (handles slashes, dashes, timestamps)
- Order status filtering (separates paid transactions from cancellations)
"""
import csv
import re
from datetime import datetime
from typing import List, Dict, Tuple, Any, Optional
from engine.models import CleanedOrder, CleanedAdRecord, InventoryItem

HEADER_ALIASES = {
    "order_id": ["子订单编号", "订单编号", "订单号", "order_id", "主订单号", "交易编号"],
    "order_time": ["下单时间", "支付时间", "创建时间", "order_time", "付款时间", "成交时间"],
    "sku_id": ["商品编码", "商家编码", "sku", "sku_id", "规格编码", "货号", "款号"],
    "sku_name": ["商品标题", "商品名称", "宝贝名称", "title", "sku_name", "产品名称"],
    "category": ["类目名称", "一级类目", "品类", "category", "商品类目", "主营类目"],
    "quantity": ["购买数量", "数量", "件数", "quantity", "销售数量", "宝贝总数量"],
    "gross_amount": ["买家实付金额", "实付金额", "订单金额", "成交金额", "amount", "销售额", "商品总价"],
    "refund_status": ["退款状态", "售后状态", "refund_status", "退款处理状态"],
    "refund_amount": ["退款金额", "退款总额", "refund_amount", "成功退款金额"],
    "order_status": ["订单当前状态", "订单状态", "交易状态", "order_status"],
    "province": ["收货省份", "省份", "收货地址省", "province", "省"],
}

ADS_HEADER_ALIASES = {
    "date": ["统计日期", "日期", "date", "投放日期"],
    "campaign_id": ["计划id", "campaign_id", "推广计划id", "广告计划id"],
    "campaign_name": ["计划名称", "推广计划", "campaign_name", "计划名"],
    "target_sku": ["主推sku", "关联商品", "target_sku", "关联sku", "主推款"],
    "spend": ["花费金额(元)", "消耗", "花费", "spend", "广告费", "总花费", "消耗金额"],
    "impressions": ["展现量", "曝光量", "impressions", "展现数", "曝光数"],
    "clicks": ["点击量", "点击数", "clicks", "有效点击"],
    "direct_gmv": ["直接引导成交金额(元)", "引导成交", "直接成交金额", "direct_gmv", "成交总金额", "直接转化金额"],
}

INVENTORY_HEADER_ALIASES = {
    "sku_id": ["商品编码", "sku_id", "货号", "商家编码", "款号"],
    "name": ["商品名称", "name", "品名", "商品标题"],
    "category": ["类目", "category", "类目名称"],
    "price": ["吊牌售价", "售价", "标价", "price"],
    "cost": ["单件采购成本(元)", "成本价", "供货价", "成本", "cost"],
    "stock": ["当前可用库存(件)", "库存量", "可用库存", "stock", "当前库存"],
    "safety_stock": ["安全库存预警线", "预警库存", "安全库存", "safety_stock"],
}

def clean_currency_str(val: Any) -> float:
    if val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip()
    s = s.replace("¥", "").replace("￥", "").replace("$", "").replace(",", "").strip()
    try:
        return float(s) if s else 0.0
    except ValueError:
        return 0.0

def parse_date_str(val: Any) -> Tuple[str, str]:
    """Returns (YYYY-MM-DD, YYYY-MM-DD HH:MM:SS)"""
    if not val:
        today = datetime.now().strftime("%Y-%m-%d")
        return today, f"{today} 00:00:00"
    s = str(val).strip().replace("/", "-")
    # Standard formats
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S"):
        try:
            dt = datetime.strptime(s[:19], fmt)
            return dt.strftime("%Y-%m-%d"), dt.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
    # Fallback to regex
    m = re.search(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})", s)
    if m:
        d_str = f"{int(m.group(1)):04d}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
        return d_str, f"{d_str} 00:00:00"
    today = datetime.now().strftime("%Y-%m-%d")
    return today, f"{today} 00:00:00"

def map_headers(file_headers: List[str], alias_dict: Dict[str, List[str]]) -> Dict[str, str]:
    mapping = {}
    normalized_headers = {h.strip().lower().replace("\ufeff", ""): h for h in file_headers}
    for standard_key, aliases in alias_dict.items():
        found = False
        for alias in aliases:
            alias_lower = alias.lower()
            if alias_lower in normalized_headers:
                mapping[standard_key] = normalized_headers[alias_lower]
                found = True
                break
        if not found:
            # Check partial contains
            for raw_lower, raw_orig in normalized_headers.items():
                if any(a.lower() in raw_lower for a in aliases):
                    mapping[standard_key] = raw_orig
                    found = True
                    break
    return mapping

class DataCleaner:
    @staticmethod
    def clean_orders(file_path: str) -> Tuple[List[CleanedOrder], Dict[str, int]]:
        cleaned_orders = []
        stats = {"total_rows": 0, "paid_orders": 0, "filtered_unpaid": 0, "refunded_orders": 0}
        
        with open(file_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            header_map = map_headers(reader.fieldnames or [], HEADER_ALIASES)
            
            for row in reader:
                stats["total_rows"] += 1
                
                order_id = str(row.get(header_map.get("order_id", ""), "")).strip()
                raw_time = row.get(header_map.get("order_time", ""), "")
                order_date, order_time = parse_date_str(raw_time)
                
                sku_id = str(row.get(header_map.get("sku_id", ""), "")).strip()
                sku_name = str(row.get(header_map.get("sku_name", ""), "")).strip()
                category = str(row.get(header_map.get("category", ""), "")).strip() or "默认品类"
                
                try:
                    quantity = max(1, int(float(row.get(header_map.get("quantity", "1"), 1) or 1)))
                except (ValueError, TypeError):
                    quantity = 1
                    
                gross_amount = clean_currency_str(row.get(header_map.get("gross_amount", ""), 0.0))
                refund_amount = clean_currency_str(row.get(header_map.get("refund_amount", ""), 0.0))
                
                order_status = str(row.get(header_map.get("order_status", ""), "")).strip()
                refund_status = str(row.get(header_map.get("refund_status", ""), "")).strip() or "无退款"
                province = str(row.get(header_map.get("province", ""), "")).strip() or "其他"
                
                # Check unpaid / canceled orders
                unpaid_keywords = ["未付款", "已关闭", "已取消", "closed", "canceled", "unpaid"]
                if any(kw in order_status.lower() for kw in unpaid_keywords):
                    stats["filtered_unpaid"] += 1
                    continue
                
                # Handle refund consistency
                is_refunded = False
                refund_keywords = ["退款", "全额退款", "售后退款", "已退款", "refunded"]
                if any(kw in refund_status.lower() for kw in refund_keywords) and refund_status != "无退款":
                    is_refunded = True
                    if refund_amount <= 0.0:
                        refund_amount = gross_amount
                    stats["refunded_orders"] += 1
                else:
                    refund_amount = 0.0
                    
                net_amount = max(0.0, round(gross_amount - refund_amount, 2))
                stats["paid_orders"] += 1
                
                cleaned_orders.append(CleanedOrder(
                    order_id=order_id,
                    order_date=order_date,
                    order_time=order_time,
                    sku_id=sku_id,
                    sku_name=sku_name,
                    category=category,
                    quantity=quantity,
                    gross_amount=round(gross_amount, 2),
                    refund_amount=round(refund_amount, 2),
                    net_amount=net_amount,
                    order_status=order_status,
                    refund_status=refund_status,
                    province=province,
                    is_valid_paid=True
                ))
                
        return cleaned_orders, stats

    @staticmethod
    def clean_ads(file_path: str) -> List[CleanedAdRecord]:
        records = []
        with open(file_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            header_map = map_headers(reader.fieldnames or [], ADS_HEADER_ALIASES)
            
            for row in reader:
                raw_date = row.get(header_map.get("date", ""), "")
                ad_date, _ = parse_date_str(raw_date)
                cmp_id = str(row.get(header_map.get("campaign_id", ""), "")).strip()
                cmp_name = str(row.get(header_map.get("campaign_name", ""), "")).strip()
                target_sku = str(row.get(header_map.get("target_sku", ""), "")).strip()
                
                spend = clean_currency_str(row.get(header_map.get("spend", ""), 0.0))
                try:
                    impressions = int(float(row.get(header_map.get("impressions", "0"), 0) or 0))
                except (ValueError, TypeError):
                    impressions = 0
                try:
                    clicks = int(float(row.get(header_map.get("clicks", "0"), 0) or 0))
                except (ValueError, TypeError):
                    clicks = 0
                direct_gmv = clean_currency_str(row.get(header_map.get("direct_gmv", ""), 0.0))
                cpc = round(spend / clicks, 2) if clicks > 0 else 0.0
                
                records.append(CleanedAdRecord(
                    date=ad_date,
                    campaign_id=cmp_id,
                    campaign_name=cmp_name,
                    target_sku=target_sku,
                    spend=round(spend, 2),
                    impressions=impressions,
                    clicks=clicks,
                    cpc=cpc,
                    direct_gmv=round(direct_gmv, 2)
                ))
        return records

    @staticmethod
    def clean_inventory(file_path: str) -> Dict[str, InventoryItem]:
        items = {}
        with open(file_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            header_map = map_headers(reader.fieldnames or [], INVENTORY_HEADER_ALIASES)
            
            for row in reader:
                sku_id = str(row.get(header_map.get("sku_id", ""), "")).strip()
                name = str(row.get(header_map.get("name", ""), "")).strip()
                category = str(row.get(header_map.get("category", ""), "")).strip()
                price = clean_currency_str(row.get(header_map.get("price", ""), 0.0))
                cost = clean_currency_str(row.get(header_map.get("cost", ""), 0.0))
                
                try:
                    stock = int(float(row.get(header_map.get("stock", "0"), 0) or 0))
                except (ValueError, TypeError):
                    stock = 0
                try:
                    safety_stock = int(float(row.get(header_map.get("safety_stock", "20"), 20) or 20))
                except (ValueError, TypeError):
                    safety_stock = 20
                    
                items[sku_id] = InventoryItem(
                    sku_id=sku_id,
                    name=name,
                    category=category,
                    price=price,
                    cost=cost,
                    stock=stock,
                    safety_stock=safety_stock
                )
        return items
