"""
Unit tests for Sales Agent CRM, Pitch Generator, and Response Handler.
"""
from engine.sales_agent.crm import init_crm_db, LeadManager
from engine.sales_agent.pitch_generator import PitchGenerator
from engine.sales_agent.dispatcher import OutreachDispatcher
from engine.sales_agent.response_handler import ResponseHandler

def test_sales_agent_flow():
    init_crm_db()
    leads = LeadManager.get_all_leads()
    assert len(leads) >= 4

    lead = leads[0]
    assert "@" in lead["contact_email"]
    assert "https://" in lead["website"]

    # Test Pitch Generator
    pitch = PitchGenerator.generate_pitch(lead)
    assert len(pitch["subject"]) > 10
    assert "https://jojo232386.github.io/autoecom-intelligence/demo.html" in pitch["body"]

    # Test Mailto command generation
    cmd = OutreachDispatcher.get_mailto_command(lead["id"])
    assert cmd.startswith('open "mailto:')
    assert lead["contact_email"] in cmd

    # Test Response Handler
    resp_pilot = ResponseHandler.handle_inquiry("We want to try the free pilot", "Acme Agency")
    assert resp_pilot["intent"] == "PILOT_REQUEST"
    assert "after format review" in resp_pilot["body"]

    resp_price = ResponseHandler.handle_inquiry("What are your monthly retainer rates?", "Acme Agency")
    assert resp_price["intent"] == "PRICING_INQUIRY"
    assert "Scope, price" in resp_price["body"]
