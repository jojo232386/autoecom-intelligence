"""
Domain data models for E-commerce Operations Automation Engine.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class CleanedOrder:
    order_id: str
    order_date: str          # YYYY-MM-DD
    order_time: str          # YYYY-MM-DD HH:MM:SS
    sku_id: str
    sku_name: str
    category: str
    quantity: int
    gross_amount: float
    refund_amount: float
    net_amount: float
    order_status: str
    refund_status: str
    province: str
    is_valid_paid: bool

@dataclass
class CleanedAdRecord:
    date: str                # YYYY-MM-DD
    campaign_id: str
    campaign_name: str
    target_sku: str
    spend: float
    impressions: int
    clicks: int
    cpc: float
    direct_gmv: float

@dataclass
class InventoryItem:
    sku_id: str
    name: str
    category: str
    price: float
    cost: Optional[float]
    stock: Optional[int]
    safety_stock: Optional[int]

@dataclass
class SKUMetrics:
    sku_id: str
    name: str
    category: str
    orders_count: int
    units_sold: int
    gmv: float
    refund_amount: float
    net_sales: float
    refund_rate_pct: float
    ad_spend: Optional[float]
    direct_ad_gmv: Optional[float]
    direct_roi: Optional[float]
    estimated_cogs: Optional[float]
    gross_profit: Optional[float]
    gross_margin_pct: Optional[float]
    current_stock: Optional[int]
    safety_stock: Optional[int]
    stock_turnover_status: str
    quadrant_tag: str        # '现金金牛', '潜力爆品', '吸血亏损', '平销防守'
    alert_flags: List[str] = field(default_factory=list)

@dataclass
class DailyMetrics:
    date: str
    orders_count: int
    units_sold: int
    gmv: float
    refunds: float
    net_sales: float
    ad_spend: Optional[float]
    direct_ad_gmv: Optional[float]
    blended_roi: Optional[float]
    gross_profit: Optional[float]
    profit_margin_pct: Optional[float]

@dataclass
class CampaignMetrics:
    campaign_id: str
    campaign_name: str
    target_sku: str
    total_spend: float
    impressions: int
    clicks: int
    overall_cpc: float
    overall_ctr_pct: float
    direct_gmv: float
    direct_roi: Optional[float]
    status_tag: str          # '高效放量', '维持观察', '控比压减'

@dataclass
class AnomalyAlert:
    level: str               # 'CRITICAL', 'WARNING', 'INFO'
    category: str            # 'ROI', 'REFUND', 'STOCK', 'CAMPAIGN'
    target: str
    metric_value: str
    threshold_value: str
    message: str
    suggested_action: str

@dataclass
class StoreSummary:
    store_name: str
    period_start: str
    period_end: str
    period_label: str
    total_orders: int
    total_units: int
    total_gmv: float
    total_refunds: float
    refund_rate_pct: float
    total_net_sales: float
    total_ad_spend: Optional[float]
    blended_roi: Optional[float]
    total_direct_ad_gmv: Optional[float]
    total_cogs: Optional[float]
    gross_profit: Optional[float]
    gross_profit_margin_pct: Optional[float]
    daily_metrics: List[DailyMetrics] = field(default_factory=list)
    sku_metrics: List[SKUMetrics] = field(default_factory=list)
    campaign_metrics: List[CampaignMetrics] = field(default_factory=list)
    anomalies: List[AnomalyAlert] = field(default_factory=list)
    executive_takeaways: List[str] = field(default_factory=list)

@dataclass
class AuditResult:
    passed: bool
    checks: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    checked_at: str = ""
