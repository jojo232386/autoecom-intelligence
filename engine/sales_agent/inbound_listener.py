"""
Autonomous Inbound Listener for GitHub Issues & Pilot Requests.
Automatically detects incoming pilot requests on the repository, adds them to CRM,
and drafts the onboarding reply.
"""
import json
import subprocess
from typing import List, Dict, Any
from engine.sales_agent.crm import init_crm_db, LeadManager
from engine.sales_agent.response_handler import ResponseHandler

REPO_NAME = "jojo232386/autoecom-intelligence"

class InboundListener:
    @staticmethod
    def check_github_issues() -> List[Dict[str, Any]]:
        cmd = f"gh issue list --repo {REPO_NAME} --json number,title,author,labels,body,createdAt --state open"
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"gh issue check error: {res.stderr}")
            return []
        try:
            return json.loads(res.stdout or "[]")
        except json.JSONDecodeError:
            return []

    @staticmethod
    def process_inbound_issues():
        init_crm_db()
        issues = InboundListener.check_github_issues()
        if not issues:
            print("No open inbound issues found on GitHub.")
            return

        for issue in issues:
            labels = [l.get("name") for l in issue.get("labels", [])]
            if "pilot-request" in labels or "commercial-lead" in labels:
                issue_num = issue["number"]
                title = issue["title"]
                body = issue.get("body", "")
                author = issue.get("author", {}).get("login", "unknown")

                print(f"Processing Inbound Pilot Request #{issue_num} from @{author}: {title}")
                # Log to CRM
                lead_data = {
                    "company_name": title.replace("[Pilot Request]:", "").strip() or author,
                    "website": f"https://github.com/{author}",
                    "niche": "Inbound GitHub Prospect",
                    "country": "Global",
                    "contact_email": f"@{author}",
                    "tier": "TIER_1",
                    "pain_point": "Inbound Pilot Request",
                    "custom_hook": "Direct GitHub Lead",
                    "personalized_subject": f"Pilot Setup for #{issue_num}",
                    "personalized_body": body[:500],
                    "status": "INBOUND_RECEIVED"
                }
                LeadManager.add_lead(lead_data)
                print(f"Logged Inbound Lead to CRM from Issue #{issue_num}")

if __name__ == "__main__":
    InboundListener.process_inbound_issues()
