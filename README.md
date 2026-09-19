# AutoEcom: reviewed single-store CSV reports

Current owner: Codex. Business goal: OPEN. External integration: BLOCKED_EXTERNAL.

Supported service: one store, agreed UTF-8 CSV format, HTML/XLSX/Markdown outputs and arithmetic checks. No source truth, net-profit, delivery-time or revenue guarantee. Missing inputs yield N/A. Refund amounts do not establish returned units or recoverable COGS; refunded orders suppress dependent cost/profit metrics pending agreed rules.

Private runtime defaults to `~/Library/Application Support/AutoEcom`; override with `AUTOECOM_DB_PATH`. Never track runtime data or credentials. `tests/fixtures` is generated synthetic data. Public Issues accept non-sensitive questions only. Historical Git versions still contain previously tracked data; this change does not rewrite history or remove already published copies.

## Local operation

Use Python 3.13+ with pytest, openpyxl and rich. `python -m pytest -q` runs isolated offline tests with synthetic customers and mocked SMTP/IMAP; it does not send mail.

`python pilot_cli.py poll` polls one private IMAP inbox read-only. Configure `PILOT_IMAP_HOST`, `PILOT_EMAIL`, `PILOT_PASSWORD` and comma-separated `PILOT_ALLOWED_SENDERS` through local environment/secrets storage. Attachment names must be exactly `orders.csv`, optional `ads.csv`, `inventory.csv`; links, code and other formats are rejected. Order columns: order_id, order_time, sku_id, quantity, amount, refund_amount, order_status; supported exact Chinese aliases are in cleaner.py. No fuzzy substring mapping. Explicit zero is required for zero refund. Duplicate order/SKU rows and invalid required data stop processing.

`python pilot_cli.py status --job ID` shows state and the output manifest hash. Review key totals against the source and inspect the four outputs in the private job folder, then `python pilot_cli.py approve --job ID --manifest-hash HASH --reviewer NAME`. No automatic approval whitelist is enabled.

After explicit authorization, set `PILOT_SMTP_HOST`, optional `PILOT_SMTP_PORT` (587), and `PILOT_SEND_AUTHORIZED` to approved recipient addresses. `python pilot_cli.py send --job ID` attaches only unchanged reviewed outputs, using STARTTLS. Exact STOP/unsubscribe/退订 in subject or plain body suppresses future sends. Review is invalidated by changed output hashes.

SMTP_ACCEPTED means the SMTP server accepted the message, not DELIVERED. SEND_FAILED can retry up to three attempts; SEND_UNKNOWN or a crash in SENDING requires provider-side reconciliation and has no automatic resend. No delivery webhook is configured; delivery and client acceptance remain unknown. Local processing restarts safely under an OS job lock. Poll is a bounded single scan of the latest 100 messages; continuous monitoring, backfill and scheduling are not enabled.

`agent_sales.py won` records an unverified payment claim only, not verified revenue. Legacy lead SMTP sending is disabled; only reviewed pilot jobs use the live sending path. Pricing, collection fees, refunds, invoice and payout evidence remain separate from engineering success.
