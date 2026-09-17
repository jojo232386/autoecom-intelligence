#!/usr/bin/env python3
"""
Command-line interface for the E-commerce Weekly Analytics White-label Automation Engine.
"""
import sys
import argparse
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from engine.pipeline import IntelligencePipeline

console = Console()

def main():
    parser = argparse.ArgumentParser(description="电商代运营多店铺经营分析与白牌周报自动化引擎")
    parser.add_argument("--orders", default="data/raw_inputs/orders_export.csv", help="订单明细导出表路径 (CSV)")
    parser.add_argument("--ads", default="data/raw_inputs/ads_spend_export.csv", help="推广消耗导出表路径 (CSV)")
    parser.add_argument("--inventory", default="data/raw_inputs/inventory_cost.csv", help="商品成本库存表路径 (CSV)")
    parser.add_argument("--store", default="美澜风尚旗舰店", help="店铺名称")
    parser.add_argument("--period", default="2026-W37周报", help="汇报周期名称")
    parser.add_argument("--agency", default="代运营白牌数字化交付中心", help="白牌交付机构名称")
    parser.add_argument("--out", default="data/deliverables", help="交付成果输出目录")

    args = parser.parse_args()

    console.print(Panel.fit(
        f"[bold cyan]极简周报[/bold cyan] · 电商代运营经营分析自动化引擎\n"
        f"[dim]白牌代工模式 · 确定性会计级勾稽自检 · 3秒全自动交付[/dim]",
        border_style="cyan"
    ))

    with console.status("[bold green]正在执行全流程自动化数据处理与勾稽审计...[/bold green]"):
        pipeline = IntelligencePipeline(
            orders_path=args.orders,
            ads_path=args.ads,
            inventory_path=args.inventory,
            store_name=args.store,
            period_label=args.period,
            agency_name=args.agency,
            output_dir=args.out
        )
        result = pipeline.run(fail_on_audit=True)

    # Render Summary Table
    summary = result["summary"]
    table = Table(title=f"📊 {args.store} 经营分析核心指标", show_header=True, header_style="bold magenta")
    table.add_column("指标类别", style="dim", width=18)
    table.add_column("数值", justify="right", style="bold")
    table.add_column("健康状态 / 说明", style="green")

    table.add_row("总成交额 (GMV)", f"¥{summary['total_gmv']:,.2f}", f"有效支付订单 {summary['total_orders']} 笔")
    table.add_row("净销售额 (Net)", f"¥{summary['total_net_sales']:,.2f}", "已剔除全部售后退款")
    refund_style = "red" if summary["refund_rate_pct"] > 15 else "yellow"
    table.add_row("退款总额 / 退款率", f"¥{summary['total_refunds']:,.2f}", f"[{refund_style}]{summary['refund_rate_pct']:.1f}%[/{refund_style}]")
    table.add_row("推广总消耗 (Ads)", f"¥{summary['total_ad_spend']:,.2f}", "全渠道付费引流总计")
    roi_style = "green" if summary["blended_roi"] >= 3.5 else "yellow"
    table.add_row("全店综合投产比 (ROI)", f"[{roi_style}]{summary['blended_roi']:.2f}[/{roi_style}]", "GMV / 推广消耗")
    table.add_row("预估商品毛利", f"¥{summary['gross_profit']:,.2f}", f"综合毛利率 [bold green]{summary['gross_profit_margin_pct']:.1f}%[/bold green]")

    console.print(table)

    # Deliverables Panel
    console.print(Panel(
        f"[bold green]✅ 全套交付件已自动生成并完成物理质检：[/bold green]\n\n"
        f"1. [bold]全屏交互式看板 (HTML)[/bold]: {result['deliverables']['html_dashboard']}\n"
        f"2. [bold]多Sheet审计级报表 (Excel)[/bold]: {result['deliverables']['excel_workbook']}\n"
        f"3. [bold]高管速递摘要 (Markdown)[/bold]: {result['deliverables']['executive_briefing']}\n"
        f"4. [bold]勾稽核验报告 (JSON)[/bold]: {result['deliverables']['audit_report']}\n",
        title="[bold green]物理闭环交付完成[/bold green]",
        border_style="green"
    ))

if __name__ == "__main__":
    main()
