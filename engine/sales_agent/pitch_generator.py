"""
Hyper-personalized B2B Pitch Generator for E-Commerce Agencies.
Generates non-spammy, highly specific outreach copy linking directly to live public demos.
"""
from typing import Dict, Any

class PitchGenerator:
    @staticmethod
    def generate_pitch(lead: Dict[str, Any]) -> Dict[str, str]:
        company_name = lead.get("company_name", "your team")
        niche = lead.get("niche", "DTC and Shopify brands")
        country = lead.get("country", "US")

        subject = f"Automating weekly client reporting for {company_name}'s Shopify brands"

        body = f"""Hi {company_name} Team,

I've been following {company_name}'s work scaling {niche}.

As your client roster expands, Monday morning client-facing reporting—merging multi-channel ad spend with net sales, tracking SKU refund rates, and calculating blended ROAS—typically eats 15+ hours of operational bandwidth every week. Moreover, manual VLOOKUP formulas occasionally break in front of brand clients.

We developed an automated white-label analytics engine specifically for e-commerce agencies that completely eliminates manual spreadsheet prep:
1. Automated Data Cleaning: Fuzzy normalizes inconsistent CSV exports, currency symbols, and mixed date formats.
2. Double-Entry Accounting Audit: Every report passes an automated balance sheet equation check (diff = 0.0) before generation, eliminating formula errors.
3. Client-Ready Deliverables: Generates both a standalone interactive HTML executive dashboard (zero-dependency, mobile-responsive, 1-click printable to PDF) and a 5-sheet audited Excel workbook in 3 seconds.

🌐 Live Interactive Demo:
You can test the actual interactive client dashboard directly in your browser:
https://jojo232386.github.io/autoecom-intelligence/demo.html
(Full portfolio: https://jojo232386.github.io/autoecom-intelligence/)

Free 1-Store Pilot:
We'd love to run a 100% free pilot for 1 of your client brands. You can send over any historical export (with sensitive customer info masked if preferred), and we will return a branded, audited interactive dashboard pack within 30 minutes for your team to review.

Would you be open to testing this on 1 store this week?

Best regards,
AutoEcom Intelligence Team
GitHub: https://github.com/jojo232386/autoecom-intelligence
"""
        return {
            "subject": subject,
            "body": body
        }
