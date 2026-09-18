"""
Autonomous Client Response Handler and Deal Closing Engine.
Analyzes incoming prospect intent and automatically drafts the exact closing response.
"""
from typing import Dict, Any

class ResponseHandler:
    @staticmethod
    def handle_inquiry(intent: str, company_name: str = "there") -> Dict[str, str]:
        intent_lower = intent.lower()

        # Intent 1: Pricing & Retainer Details (check first)
        if any(w in intent_lower for w in ["pricing", "cost", "how much", "rate", "fee", "retainer", "price"]):
            subject = f"Re: White-Label Reporting Packages for {company_name}"
            body = f"""Hi {company_name} Team,

Here is our transparent, fixed-price white-label agency structure:

1. Single Store Pilot / Ad-Hoc:
- $99 USD / run (or 100% free for your first trial store).

2. Agency Monthly Retainer (Most Popular):
- Starter: $499 USD / month (covers up to 5 client stores, 4 weekly reports + 1 monthly rollup per store).
- Growth: $899 USD / month (covers up to 12 client stores, custom KPI mapping, priority 1-hour Monday delivery).
- Enterprise: $1,499 USD / month (unlimited client stores, dedicated adapter support).

Every package includes:
- 100% white-label delivery (your agency logo and branding).
- Automated double-entry audit (diff = 0.0 guarantee).
- Free schema maintenance if client platforms update export formats.

Would you like to test the free 1-store pilot first to verify the quality before deciding on a package?

Best regards,
AutoEcom Intelligence Team
"""
            return {"subject": subject, "body": body, "intent": "PRICING_INQUIRY"}

        # Intent 2: Interested in Free Pilot / How to start
        elif any(w in intent_lower for w in ["pilot", "sample", "start", "try", "interested", "how does it work"]):
            subject = f"Re: Free 1-Store Pilot Setup for {company_name}"
            body = f"""Hi {company_name} Team,

Glad to hear from you! Setting up the free pilot is completely frictionless:

1. Data Export:
Simply send over an exported CSV or Excel sheet for 1 store (order dump, ad spend, or weekly summary). Feel free to mask customer names or addresses—our engine only requires item quantities, amounts, dates, and campaign spends.

2. Automated Turnaround:
Within 30 minutes of receipt, we will run the data through our pipeline and deliver:
- A standalone, branded interactive HTML dashboard (responsive on mobile & desktop).
- A 5-sheet reconciled Excel workbook (.xlsx) with balance checks.
- A 60-second executive summary ready to paste into Slack or send to the client.

3. Zero Commitment:
Your team can review the output. If you love it, we can discuss ongoing weekly white-label coverage. If not, the dashboard is yours to keep with zero obligation.

Whenever you're ready, feel free to reply with the file attached or a Google Drive link!

Best regards,
AutoEcom Intelligence Team
"""
            return {"subject": subject, "body": body, "intent": "PILOT_REQUEST"}

        # Fallback: General Technical or Custom Format Questions
        else:
            subject = f"Re: Weekly Reporting Automation for {company_name}"
            body = f"""Hi {company_name} Team,

Thank you for reaching out! 

Our engine is built with a flexible fuzzy mapping layer specifically designed to ingest non-standard ERP, Shopify, Amazon, and multi-channel ad formats without manual schema recoding.

Could you share 5 to 10 sample rows or a header snippet of your typical export? We will verify the schema compatibility immediately and send back a confirmed ingestion preview.

Best regards,
AutoEcom Intelligence Team
"""
            return {"subject": subject, "body": body, "intent": "TECHNICAL_INQUIRY"}
