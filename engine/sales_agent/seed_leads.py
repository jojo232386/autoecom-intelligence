"""
Populate the CRM database with verified target e-commerce agencies and auto-generate personalized pitches.
"""
from engine.sales_agent.crm import init_crm_db, LeadManager
from engine.sales_agent.pitch_generator import PitchGenerator

INITIAL_LEADS = [
    {
        "company_name": "Barrel",
        "website": "https://www.barrelny.com",
        "niche": "DTC eCommerce & Shopify brands",
        "country": "US",
        "contact_email": "newbiz@barrelny.com",
        "tier": "TIER_1",
        "pain_point": "Multi-client weekly report compilation and ROAS reconciliation",
        "custom_hook": "Scaling high-growth consumer brands on Shopify",
    },
    {
        "company_name": "Eastside Co",
        "website": "https://eastsideco.com",
        "niche": "Shopify Plus enterprise retailers",
        "country": "UK",
        "contact_email": "info@eastsideco.com",
        "tier": "TIER_1",
        "pain_point": "Weekly client business intelligence dashboards and SKU return rate diagnosis",
        "custom_hook": "Managing high-volume international Shopify Plus stores",
    },
    {
        "company_name": "Commerce UI",
        "website": "https://commerce-ui.com",
        "niche": "Headless Shopify & performance commerce",
        "country": "Global",
        "contact_email": "hello@commerce-ui.com",
        "tier": "TIER_1",
        "pain_point": "Client reporting automation and margin auditing",
        "custom_hook": "Boutique high-touch technical client management",
    },
    {
        "company_name": "Hashmeta",
        "website": "https://hashmeta.com",
        "niche": "Social & cross-border eCommerce operations",
        "country": "Singapore",
        "contact_email": "contact@hashmeta.com",
        "tier": "TIER_2",
        "pain_point": "Multi-channel ad spend consolidation and weekly GMV tracking",
        "custom_hook": "Multi-region DTC and cross-border store scaling",
    }
]

def seed_database():
    init_crm_db()
    existing = LeadManager.get_all_leads()
    if existing:
        print(f"CRM database already contains {len(existing)} leads. Skipping seed.")
        return

    for l in INITIAL_LEADS:
        pitch = PitchGenerator.generate_pitch(l)
        lead_record = {
            **l,
            "personalized_subject": pitch["subject"],
            "personalized_body": pitch["body"],
            "status": "PITCH_READY"
        }
        lead_id = LeadManager.add_lead(lead_record)
        print(f"Seeded Lead #{lead_id}: {l['company_name']} ({l['contact_email']}) -> PITCH_READY")

if __name__ == "__main__":
    seed_database()
