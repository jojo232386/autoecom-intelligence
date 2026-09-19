"""Draft-only replies for the supported narrow service."""
class ResponseHandler:
    @staticmethod
    def handle_inquiry(intent, company_name="there"):
        kind = "PRICING_INQUIRY" if any(w in intent.lower() for w in ["price", "rate", "cost", "retainer"]) else "PILOT_REQUEST"
        return {"intent": kind, "subject": "Re: Fixed-format CSV reporting",
                "body": "We support a reviewed single-store CSV reporting pilot. Scope, price, timeline and revision limits are confirmed after format review. Private intake must be configured before sending samples. Do not post operating data or private links in public issues. Missing inputs will be marked N/A."}
