#!/usr/bin/env python3
"""
Autonomous Commercial Sales Agent CLI.
Commands:
- status: Shows all prospects, pipeline stages, and revenue in CRM
- dispatch: Automatically stages an outreach email for a prospect in macOS mail client
- reply: Ingests an incoming client message and outputs the exact tailored closing response
- won: Records verified revenue collected from a customer
"""
import sys
import argparse
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from engine.sales_agent.crm import init_crm_db, LeadManager
from engine.sales_agent.dispatcher import OutreachDispatcher
from engine.sales_agent.response_handler import ResponseHandler

console = Console()

def main():
    init_crm_db()
    parser = argparse.ArgumentParser(description="Autonomous B2B Commercial Sales Agent")
    subparsers = parser.add_subparsers(dest="command", help="Sales Agent Action")

    # Status
    subparsers.add_parser("status", help="View active CRM prospect pipeline and revenue")

    # Dispatch
    dispatch_parser = subparsers.add_parser("dispatch", help="Stage or send outreach to a target lead")
    dispatch_parser.add_argument("--id", type=int, required=True, help="Lead ID from CRM")

    # Reply
    reply_parser = subparsers.add_parser("reply", help="Generate response to incoming client message")
    reply_parser.add_argument("--company", type=str, default="Client", help="Company name")
    reply_parser.add_argument("--text", type=str, required=True, help="Incoming message content")

    # Won
    won_parser = subparsers.add_parser("won", help="Record real revenue collected")
    won_parser.add_argument("--id", type=int, required=True, help="Lead ID")
    won_parser.add_argument("--amount", type=float, required=True, help="Actual cash amount collected")
    won_parser.add_argument("--currency", type=str, default="USD", help="Currency (USD/RMB)")

    args = parser.parse_args()

    if args.command == "status" or not args.command:
        leads = LeadManager.get_all_leads()
        total_rev_usd = sum(l["revenue_collected"] for l in leads if l["currency"] == "USD")
        total_rev_cny = sum(l["revenue_collected"] for l in leads if l["currency"] == "RMB")

        console.print(Panel.fit(
            f"[bold cyan]AutoEcom Sales Agent · B2B Enterprise Pipeline[/bold cyan]\n"
            f"[dim]Verified Inbound/Outbound Funnels · Active CRM Prospects: {len(leads)}[/dim]\n"
            f"[bold green]Verified Net Revenue Collected: ${total_rev_usd:.2f} USD | ¥{total_rev_cny:.2f} RMB[/bold green]",
            border_style="cyan"
        ))

        table = Table(title="🎯 Active Enterprise Prospects & Pipeline Stages", show_header=True, header_style="bold magenta")
        table.add_column("ID", style="dim", width=4)
        table.add_column("企业名称", style="bold", width=16)
        table.add_column("业务定位 / 客户群", width=26)
        table.add_column("商务邮箱 / 渠道", width=24)
        table.add_column("状态", style="cyan", width=14)
        table.add_column("已收款", justify="right", style="green", width=12)

        for l in leads:
            status_style = "green" if l["status"] == "WON" else ("blue" if l["status"] == "DISPATCHED" else "yellow")
            table.add_row(
                str(l["id"]),
                l["company_name"],
                l["niche"],
                l["contact_email"],
                f"[{status_style}]{l['status']}[/{status_style}]",
                f"${l['revenue_collected']:.2f}" if l["currency"] == "USD" else f"¥{l['revenue_collected']:.2f}"
            )
        console.print(table)

    elif args.command == "dispatch":
        success = OutreachDispatcher.stage_outreach_macos(args.id)
        if success:
            console.print(Panel(
                f"[bold green]✅ 针对 Lead #{args.id} 的专属商务邮件已在系统邮件客户端中自动装载！[/bold green]\n"
                f"[dim]收件人、定制主题、正文、公网演示链接已全自动预填完毕。无需手动复制粘贴，一键即可发出。[/dim]",
                border_style="green"
            ))
        else:
            console.print(f"[bold red]❌ Failed to stage outreach for Lead #{args.id}[/bold red]")

    elif args.command == "reply":
        resp = ResponseHandler.handle_inquiry(args.text, args.company)
        console.print(Panel(
            f"[bold yellow]检测到意向类型: {resp['intent']}[/bold yellow]\n\n"
            f"[bold cyan]Subject:[/bold cyan] {resp['subject']}\n\n"
            f"{resp['body']}",
            title=f"🤖 自动生成的成交谈判回复 ({args.company})",
            border_style="blue"
        ))

    elif args.command == "won":
        LeadManager.record_revenue(args.id, args.amount, args.currency)
        console.print(f"[bold green]🎉 真实到账成功入库: Lead #{args.id} 支付 {args.currency} {args.amount}！[/bold green]")

if __name__ == "__main__":
    main()
