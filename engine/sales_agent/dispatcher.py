"""
Automated Dispatcher for B2B Direct Outreach.
Handles both headless SMTP sending and 1-command zero-typing native mailto staging.
"""
import urllib.parse
import subprocess
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
from engine.sales_agent.crm import LeadManager, get_db_connection

class OutreachDispatcher:
    @staticmethod
    def get_mailto_command(lead_id: int) -> str:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM leads WHERE id = ?", (lead_id,))
        lead = cursor.fetchone()
        conn.close()

        if not lead:
            raise ValueError(f"Lead ID {lead_id} not found")

        recipient = lead["contact_email"]
        subject = lead["personalized_subject"]
        body = lead["personalized_body"]

        encoded_subject = urllib.parse.quote(subject)
        encoded_body = urllib.parse.quote(body)
        mailto_url = f"mailto:{recipient}?subject={encoded_subject}&body={encoded_body}"

        return f'open "{mailto_url}"'

    @staticmethod
    def stage_outreach_macos(lead_id: int) -> bool:
        """Opens the user's native mail client with the fully drafted, personalized pitch pre-filled."""
        cmd = OutreachDispatcher.get_mailto_command(lead_id)
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if res.returncode == 0:
            LeadManager.update_lead_status(lead_id, "QUEUED", notes="Staged in macOS default mail client")
            return True
        return False

    @staticmethod
    def send_headless_smtp(
        lead_id: int,
        smtp_host: str,
        smtp_port: int,
        sender_email: str,
        sender_password: str,
        use_tls: bool = True
    ) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM leads WHERE id = ?", (lead_id,))
        lead = cursor.fetchone()
        conn.close()

        if not lead:
            raise ValueError(f"Lead ID {lead_id} not found")

        recipient = lead["contact_email"]
        subject = lead["personalized_subject"]
        body = lead["personalized_body"]

        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = recipient
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))

        server = smtplib.SMTP(smtp_host, smtp_port, timeout=15)
        if use_tls:
            server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()

        LeadManager.update_lead_status(lead_id, "DISPATCHED", notes="Sent headlessly via SMTP")
        return True
