"""Evidence-limited diagnostics; no profitability or stock forecasts from missing inputs."""
class InsightEngine:
    @staticmethod
    def generate_diagnostics(summary):
        notes = [f"GMV ¥{summary.total_gmv:,.2f}；退款 ¥{summary.total_refunds:,.2f}；净销售额 ¥{summary.total_net_sales:,.2f}。净销售额不代表到账。"]
        if summary.gross_profit is None:
            notes.append("广告后贡献利润 N/A：成本、广告记录或退款退货成本规则不足；暂停利润结论。")
        else:
            notes.append(f"广告后贡献利润 ¥{summary.gross_profit:,.2f}（净销售减采购成本和广告，不含其他费用，非净利润）。")
        if any(s.current_stock is None or s.safety_stock is None for s in summary.sku_metrics):
            notes.append("部分库存或预警线未提供：暂停相关库存结论。")
        return [], notes
