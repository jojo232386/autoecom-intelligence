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
        from engine.sales_agent.pitch_generator import PitchGenerator
        pitch = PitchGenerator.generate_pitch(dict(lead))
        subject = pitch["subject"]
        body = pitch["body"]

        encoded_subject = urllib.parse.quote(subject)
        encoded_body = urllib.parse.quote(body)
        mailto_url = f"mailto:{recipient}?subject={encoded_subject}&body={encoded_body}"

        return f'open "{mailto_url}"'

    @staticmethod
    def stage_outreach_macos(lead_id: int) -> bool:
        """Opens the user's native mail client with the fully drafted, personalized pitch pre-filled."""
        cmd = OutreachDispatcher.get_mailto_command(lead_id)
        res = subprocess.run(["open", cmd[len('open "'):-1]], capture_output=True, text=True)
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
        raise RuntimeError("Direct lead sending disabled: use reviewed pilot job with recipient authorization")

    @staticmethod
    def send_message_smtp(msg, smtp_host, smtp_port, sender_email, sender_password):
        """SMTP acceptance is not delivery. Only failures known to precede DATA are retryable."""
        server = None
        phase = 'CONNECT'
        try:
            server = smtplib.SMTP(smtp_host, smtp_port, timeout=20)
            server.starttls()
            server.login(sender_email, sender_password)
            phase = 'DATA'
            refused = server.send_message(msg)
            if refused:
                return {'state': 'SEND_FAILED', 'evidence': 'recipient_refused', 'message_id': msg['Message-ID']}
            return {'state': 'SMTP_ACCEPTED', 'evidence': 'SMTP send_message returned without refusal', 'message_id': msg['Message-ID']}
        except (smtplib.SMTPRecipientsRefused, smtplib.SMTPDataError) as exc:
            return {'state': 'SEND_FAILED', 'error_type': type(exc).__name__, 'message_id': msg['Message-ID']}
        except Exception as exc:
            return {'state': 'SEND_UNKNOWN' if phase == 'DATA' else 'SEND_FAILED', 'error_type': type(exc).__name__, 'message_id': msg['Message-ID']}
        finally:
            if server is not None:
                try:
                    server.close()
                except Exception:
                    pass
