"""
Autonomous B2B CRM and Lead Management Engine.
Manages prospect discovery, personalized pitch generation, dispatch status, and revenue tracking.
"""
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_PATH = "data/crm.sqlite3"

def get_db_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_crm_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT NOT NULL,
        website TEXT,
        niche TEXT,
        country TEXT,
        contact_email TEXT,
        tier TEXT DEFAULT 'TIER_1',
        pain_point TEXT,
        custom_hook TEXT,
        personalized_subject TEXT,
        personalized_body TEXT,
        status TEXT DEFAULT 'DISCOVERED', -- DISCOVERED, PITCH_READY, QUEUED, DISPATCHED, REPLIED, WON, CLOSED
        dispatched_at TIMESTAMP,
        response_summary TEXT,
        revenue_collected REAL DEFAULT 0.0,
        currency TEXT DEFAULT 'USD',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

class LeadManager:
    @staticmethod
    def add_lead(lead_data: Dict[str, Any]) -> int:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO leads (
            company_name, website, niche, country, contact_email, tier, 
            pain_point, custom_hook, personalized_subject, personalized_body, status
        ) VALUES (
            :company_name, :website, :niche, :country, :contact_email, :tier,
            :pain_point, :custom_hook, :personalized_subject, :personalized_body, :status
        )
        """, lead_data)
        lead_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return lead_id

    @staticmethod
    def get_all_leads(status: Optional[str] = None) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        if status:
            cursor.execute("SELECT * FROM leads WHERE status = ? ORDER BY id ASC", (status,))
        else:
            cursor.execute("SELECT * FROM leads ORDER BY id ASC")
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

    @staticmethod
    def update_lead_status(lead_id: int, status: str, notes: Optional[str] = None):
        conn = get_db_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        if status == "DISPATCHED":
            cursor.execute("UPDATE leads SET status = ?, dispatched_at = ?, updated_at = ? WHERE id = ?", (status, now, now, lead_id))
        else:
            cursor.execute("UPDATE leads SET status = ?, response_summary = COALESCE(?, response_summary), updated_at = ? WHERE id = ?", (status, notes, now, lead_id))
        conn.commit()
        conn.close()

    @staticmethod
    def record_revenue(lead_id: int, amount: float, currency: str = "USD"):
        conn = get_db_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute("UPDATE leads SET revenue_collected = revenue_collected + ?, currency = ?, status = 'WON', updated_at = ? WHERE id = ?", (amount, currency, now, lead_id))
        conn.commit()
        conn.close()
