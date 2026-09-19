"""
Populate the CRM database with unverified candidate agencies and auto-generate personalized pitches.
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
    },
    {
        "company_name": "Avex Designs",
        "website": "https://avexdesigns.com",
        "niche": "Luxury, fashion & lifestyle Shopify Plus DTC brands",
        "country": "US",
        "contact_email": "newbusiness@avexdesigns.com",
        "tier": "TIER_1",
        "pain_point": "High-touch weekly client reporting and gross margin auditing",
        "custom_hook": "Scaling premier fashion and DTC retail accounts",
    },
    {
        "company_name": "MindArc",
        "website": "https://mindarc.com.au",
        "niche": "High-volume Australian Shopify Plus retailers",
        "country": "Australia",
        "contact_email": "hello@mindarc.com.au",
        "tier": "TIER_1",
        "pain_point": "Multi-store weekly operational reporting and inventory health monitoring",
        "custom_hook": "Powering leading Australian enterprise eCommerce brands",
    },
    {
        "company_name": "Overdose. Digital",
        "website": "https://overdose.digital",
        "niche": "Global digital commerce & retail operations",
        "country": "Global",
        "contact_email": "hello@overdose.digital",
        "tier": "TIER_1",
        "pain_point": "Consolidating disparate analytics spreadsheets into executive dashboards",
        "custom_hook": "Global multi-region retail and DTC transformation",
    },
    {
        "company_name": "blubolt",
        "website": "https://blubolt.com",
        "niche": "Fast-growing UK Shopify Plus brands",
        "country": "UK",
        "contact_email": "hello@blubolt.com",
        "tier": "TIER_2",
        "pain_point": "Weekly client marketing ROAS and SKU-level profit tracking",
        "custom_hook": "Accelerating UK fashion and lifestyle eCommerce growth",
    }
]

def seed_database():
    init_crm_db()
    existing = LeadManager.get_all_leads()
    existing_emails = {l["contact_email"] for l in existing}

    added = 0
    for l in INITIAL_LEADS:
        if l["contact_email"] in existing_emails:
            continue
        pitch = PitchGenerator.generate_pitch(l)
        lead_record = {
            **l,
            "personalized_subject": pitch["subject"],
            "personalized_body": pitch["body"],
            "status": "UNVERIFIED_CANDIDATE"
        }
        lead_id = LeadManager.add_lead(lead_record)
        print(f"Seeded Lead #{lead_id}: {l['company_name']} ({l['contact_email']}) -> PITCH_READY")
        added += 1

    print(f"Database sync complete. Total active leads in CRM: {len(LeadManager.get_all_leads())} (Added: {added})")

if __name__ == "__main__":
    seed_database()
