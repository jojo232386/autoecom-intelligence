"""Draft template; no claim that a prospect has a known pain or buying intent."""
class PitchGenerator:
    @staticmethod
    def generate_pitch(lead):
        return {"subject": "Single-store CSV reporting pilot",
                "body": f"Hi {lead.get('company_name', 'there')},\nWe have a synthetic demo of fixed-format CSV reporting: https://jojo232386.github.io/autoecom-intelligence/demo.html . If this is relevant to your reporting work, we can discuss a small reviewed pilot. Scope, price and timeline follow sample review. Please do not post operating data in public issues. Reply STOP if you do not want further contact."}
