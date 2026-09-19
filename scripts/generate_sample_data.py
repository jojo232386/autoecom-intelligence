"""
Generate realistic, high-fidelity e-commerce export files with real-world edge cases.
Includes:
- orders_export.csv (multi-platform order dump with dirty formatting, mixed dates, refunds, cancellations)
- ads_spend_export.csv (campaign traffic, CPC, clicks, spend, direct GMV)
- inventory_cost.csv (COGS, available stock, category)
"""
import csv
from pathlib import Path
Path("tests/fixtures").mkdir(parents=True, exist_ok=True)
import random
from datetime import datetime, timedelta

random.seed(42)

SKUS = [
    {"sku_id": "SKU-001", "name": "法式复古碎花连衣裙", "category": "连衣裙", "price": 289.0, "cost": 85.0, "stock": 42}, # bestseller, low stock alert!
    {"sku_id": "SKU-002", "name": "垂感显瘦西装阔腿裤", "category": "裤装", "price": 199.0, "cost": 55.0, "stock": 350},
    {"sku_id": "SKU-003", "name": "极简纯色真丝衬衫", "category": "上衣", "price": 369.0, "cost": 110.0, "stock": 180},
    {"sku_id": "SKU-004", "name": "宽松廓形针织开衫", "category": "毛织", "price": 219.0, "cost": 65.0, "stock": 210}, # high refund rate
    {"sku_id": "SKU-005", "name": "羊毛混纺双面呢大衣", "category": "外套", "price": 899.0, "cost": 310.0, "stock": 95},
    {"sku_id": "SKU-006", "name": "蕾丝打底吊带背心", "category": "内搭", "price": 79.0, "cost": 18.0, "stock": 580},
    {"sku_id": "SKU-007", "name": "高腰微喇牛仔裤", "category": "裤装", "price": 189.0, "cost": 50.0, "stock": 400}, # ad burn, low conversion
    {"sku_id": "SKU-008", "name": "优雅收腰风衣外套", "category": "外套", "price": 559.0, "cost": 175.0, "stock": 120},
    {"sku_id": "SKU-009", "name": "经典小香风编织外套", "category": "外套", "price": 439.0, "cost": 130.0, "stock": 160},
    {"sku_id": "SKU-010", "name": "基础款莫代尔打底衫", "category": "内搭", "price": 89.0, "cost": 22.0, "stock": 650},
]

CAMPAIGNS = [
    {"campaign_id": "CMP-101", "name": "万相台-全店爆款智投", "target_sku": "SKU-001", "daily_budget": 850},
    {"campaign_id": "CMP-102", "name": "直通车-精准人群高转化", "target_sku": "SKU-002", "daily_budget": 600},
    {"campaign_id": "CMP-103", "name": "千川-短视频种草引流", "target_sku": "SKU-003", "daily_budget": 500},
    {"campaign_id": "CMP-104", "name": "引力魔方-新客拉新", "target_sku": "SKU-007", "daily_budget": 950}, # burn!
    {"campaign_id": "CMP-105", "name": "品销宝-品牌词专区", "target_sku": "ALL", "daily_budget": 300},
]

PROVINCES = ["浙江省", "广东省", "江苏省", "上海市", "山东省", "四川省", "北京市", "湖北省", "福建省", "河南省"]

def generate_orders():
    start_date = datetime(2026, 9, 8)
    orders = []
    order_counter = 10001
    
    for day_offset in range(7):
        current_day = start_date + timedelta(days=day_offset)
        # 40 to 60 orders per day
        daily_order_count = random.randint(45, 65)
        for _ in range(daily_order_count):
            order_id = f"TB202609{order_counter}"
            order_counter += 1
            
            # Weight bestselling skus higher
            sku_weights = [0.28, 0.16, 0.12, 0.10, 0.06, 0.09, 0.04, 0.05, 0.05, 0.05]
            sku = random.choices(SKUS, weights=sku_weights)[0]
            
            qty = 1 if random.random() > 0.12 else 2
            item_price = sku["price"]
            total_amount = item_price * qty
            
            # Date formatting edge case: mix hyphen and slash formats, add seconds
            hour = random.randint(8, 23)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            time_obj = current_day.replace(hour=hour, minute=minute, second=second)
            if random.random() > 0.4:
                order_time = time_obj.strftime("%Y-%m-%d %H:%M:%S")
            else:
                order_time = time_obj.strftime("%Y/%m/%d %H:%M:%S")
                
            # Order status
            # 5% unpaid/closed (should be filtered out by cleaner)
            # 95% paid/completed
            rand_val = random.random()
            if rand_val < 0.05:
                order_status = "已关闭(买家未付款)"
                refund_status = "无退款"
                refund_amount = 0.0
            else:
                order_status = "买家已付款" if day_offset >= 5 else "交易成功"
                
                # Refund logic: SKU-004 has 26% refund rate, others average 8-12%
                sku_refund_prob = 0.28 if sku["sku_id"] == "SKU-004" else 0.09
                if random.random() < sku_refund_prob:
                    refund_status = random.choice(["已全额退款", "售后退款成功", "仅退款(已到账)"])
                    refund_amount = total_amount
                else:
                    refund_status = "无退款"
                    refund_amount = 0.0
            
            # Dirty data injection: some trailing whitespaces or currency symbols
            amount_str = f"{total_amount:.2f}"
            if random.random() < 0.15:
                amount_str = f" ¥{amount_str} "
            elif random.random() < 0.1:
                amount_str = f"{amount_str}  "
                
            orders.append({
                "子订单编号": order_id,
                "下单时间": order_time,
                "商品编码": sku["sku_id"],
                "商品标题": sku["name"],
                "类目名称": sku["category"],
                "购买数量": qty,
                "买家实付金额": amount_str,
                "退款状态": refund_status,
                "退款金额": f"{refund_amount:.2f}",
                "订单当前状态": order_status,
                "收货省份": random.choice(PROVINCES),
            })
            
    with open("tests/fixtures/orders_export.csv", "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(orders[0].keys()))
        writer.writeheader()
        writer.writerows(orders)
    print(f"Generated {len(orders)} orders into tests/fixtures/orders_export.csv")

def generate_ads():
    start_date = datetime(2026, 9, 8)
    ads = []
    
    for day_offset in range(7):
        current_day = start_date + timedelta(days=day_offset)
        date_str = current_day.strftime("%Y-%m-%d")
        
        for cmp in CAMPAIGNS:
            budget = cmp["daily_budget"]
            # Fluctuating actual spend
            actual_spend = round(budget * random.uniform(0.88, 1.08), 2)
            
            # Impressions & CPC
            cpc = random.uniform(1.2, 2.8)
            clicks = int(actual_spend / cpc)
            ctr = random.uniform(0.025, 0.055)
            impressions = int(clicks / ctr)
            
            # Direct GMV generated
            if cmp["campaign_id"] == "CMP-101": # High ROI
                roi = random.uniform(3.8, 5.2)
            elif cmp["campaign_id"] == "CMP-102":
                roi = random.uniform(2.9, 3.8)
            elif cmp["campaign_id"] == "CMP-103":
                roi = random.uniform(2.1, 2.9)
            elif cmp["campaign_id"] == "CMP-104": # Burn money pit!
                roi = random.uniform(0.75, 1.25)
            else:
                roi = random.uniform(3.5, 4.5)
                
            direct_gmv = round(actual_spend * roi, 2)
            
            ads.append({
                "统计日期": date_str,
                "计划ID": cmp["campaign_id"],
                "计划名称": cmp["name"],
                "主推SKU": cmp["target_sku"],
                "花费金额(元)": actual_spend,
                "展现量": impressions,
                "点击量": clicks,
                "点击单价CPC(元)": round(actual_spend / clicks, 2) if clicks > 0 else 0.0,
                "直接引导成交金额(元)": direct_gmv,
            })
            
    with open("tests/fixtures/ads_spend_export.csv", "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(ads[0].keys()))
        writer.writeheader()
        writer.writerows(ads)
    print(f"Generated {len(ads)} ad campaign logs into tests/fixtures/ads_spend_export.csv")

def generate_inventory():
    rows = []
    for s in SKUS:
        rows.append({
            "商品编码": s["sku_id"],
            "商品名称": s["name"],
            "类目": s["category"],
            "吊牌售价": s["price"],
            "单件采购成本(元)": s["cost"],
            "当前可用库存(件)": s["stock"],
            "安全库存预警线": 50 if s["sku_id"] == "SKU-001" else 30
        })
    with open("tests/fixtures/inventory_cost.csv", "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Generated {len(rows)} SKU inventory records into tests/fixtures/inventory_cost.csv")

if __name__ == "__main__":
    generate_orders()
    generate_ads()
    generate_inventory()
