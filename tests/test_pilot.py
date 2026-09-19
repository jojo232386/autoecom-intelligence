from email.message import EmailMessage
from pathlib import Path
import smtplib
import pytest
from engine.sales_agent.pilot import Pilot, digest
from engine.sales_agent.dispatcher import OutreachDispatcher
from engine.cleaner import DataCleaner
from engine.analyzer import DataAnalyzer
from engine.pipeline import IntelligencePipeline

CSV = b'order_id,order_time,sku_id,sku_name,quantity,amount,refund_amount,order_status\n1,2026-09-01,A,Test,2,100,20,paid\n'
CONFIG = dict(smtp_host='smtp.example.com', smtp_port=587, sender_email='sender@example.com', sender_password='TEST')

def mail(sender='buyer@example.com', payload=CSV, name='orders.csv', subject='Pilot'):
    msg = EmailMessage()
    msg['From'] = sender
    msg['Subject'] = subject
    msg.set_content('Please process this TEST sample')
    if name:
        msg.add_attachment(payload, maintype='text', subtype='csv', filename=name)
    return msg.as_bytes()

def ingest(pilot, **kwargs):
    return pilot.ingest(mail(**kwargs), 'uid-1', ['buyer@example.com', 'other@example.com'])

def approved():
    pilot = Pilot()
    job = ingest(pilot)
    assert pilot.process(job) == 'REVIEW_REQUIRED'
    pilot.approve(job, digest(pilot.get(job)['manifest'].encode()), 'TEST reviewer')
    return pilot, job

def test_missing_and_partial_refund(tmp_path):
    file = tmp_path / 'orders.csv'
    file.write_bytes(CSV)
    orders, _ = DataCleaner.clean_orders(str(file))
    assert orders[0].refund_amount == 20
    summary = DataAnalyzer.analyze(orders, [], {})
    assert summary.total_net_sales == 80
    assert summary.total_cogs is None
    assert summary.gross_profit is None
    assert summary.total_ad_spend is None
    assert summary.sku_metrics[0].current_stock is None
    assert summary.sku_metrics[0].stock_turnover_status == '未提供'
    inventory = tmp_path / 'inv.csv'
    inventory.write_text('sku_id,cost,stock,safety_stock\nA,30,0,10\n')
    inv = DataCleaner.clean_inventory(str(inventory))
    summary = DataAnalyzer.analyze(orders, [], inv)
    assert summary.total_cogs is None  # No assumption that refund returned goods.
    orders[0].refund_amount = 0
    summary = DataAnalyzer.analyze(orders, [], inv)
    assert summary.total_cogs == 60
    assert summary.sku_metrics[0].current_stock == 0
    assert summary.gross_profit is None  # No ads supplied.
    inventory.write_text('sku_id,cost,stock,safety_stock\nA,,,\n')
    inv = DataCleaner.clean_inventory(str(inventory))
    assert inv['A'].cost is None and inv['A'].stock is None

def test_repeat_restart_and_isolation():
    pilot = Pilot()
    job = ingest(pilot)
    assert ingest(Pilot()) == job
    other = ingest(pilot, sender='other@example.com')
    assert other != job and pilot.path(other).parent != pilot.path(job).parent
    assert pilot.process(job) == 'REVIEW_REQUIRED'
    assert Pilot().process(job) == 'REVIEW_REQUIRED'
    assert Pilot().get(other)['state'] == 'RECEIVED'

def test_reject_path_code_and_unapproved_sender():
    pilot = Pilot()
    for name in ('../orders.csv', '/tmp/orders.csv', 'run.py', 'data.xlsx'):
        with pytest.raises(ValueError):
            ingest(pilot, name=name)
    with pytest.raises(ValueError):
        ingest(pilot, sender='stranger@example.com')

def test_review_gate_tamper_and_audit_failure(monkeypatch):
    pilot = Pilot()
    job = ingest(pilot)
    with pytest.raises(ValueError):
        pilot.send(job, CONFIG, ['buyer@example.com'])
    monkeypatch.setattr(IntelligencePipeline, 'run', lambda *a, **k: {'audit_passed': False})
    assert pilot.process(job) == 'QA_FAILED'
    with pytest.raises(ValueError):
        pilot.approve(job, 'wrong', 'TEST')
    with pytest.raises(ValueError):
        pilot.send(job, CONFIG, ['buyer@example.com'])

def test_post_review_tamper_blocked():
    pilot, job = approved()
    (pilot.path(job)/'output/weekly_report.xlsx').write_bytes(b'changed')
    with pytest.raises(ValueError):
        pilot.send(job, CONFIG, ['buyer@example.com'])

def test_unsubscribe_before_send():
    pilot, job = approved()
    assert ingest(pilot, subject='STOP', name=None) == 'SUPPRESSED'
    with pytest.raises(ValueError):
        Pilot().send(job, CONFIG, ['buyer@example.com'])

class SMTP:
    failure = None
    calls = 0
    def __init__(self, *a, **kw): pass
    def starttls(self): pass
    def login(self, *a): pass
    def close(self): pass
    def send_message(self, msg):
        type(self).calls += 1
        if self.failure:
            raise self.failure
        assert len(list(msg.iter_attachments())) == 4
        return {}

@pytest.mark.parametrize('failure,state', [(None,'SMTP_ACCEPTED'), (TimeoutError(),'SEND_UNKNOWN'),
    (smtplib.SMTPDataError(450,b'Temporary failure'),'SEND_FAILED')])
def test_send_evidence_and_retry(monkeypatch, failure, state):
    SMTP.failure = failure
    SMTP.calls = 0
    monkeypatch.setattr(smtplib, 'SMTP', SMTP)
    pilot, job = approved()
    result = pilot.send(job, CONFIG, ['buyer@example.com'])
    assert result['state'] == state
    if state == 'SEND_FAILED':
        pilot.send(job, CONFIG, ['buyer@example.com'])
        pilot.send(job, CONFIG, ['buyer@example.com'])
    with pytest.raises(ValueError):
        Pilot().send(job, CONFIG, ['buyer@example.com'])
    assert SMTP.calls == (3 if state == 'SEND_FAILED' else 1)

def test_crash_during_send_blocks_retry():
    pilot, job = approved()
    pilot.state(job, 'SENDING')
    with pytest.raises(ValueError):
        Pilot().send(job, CONFIG, ['buyer@example.com'])

def test_private_intake_closed_without_config(monkeypatch):
    monkeypatch.delenv('PILOT_IMAP_HOST', raising=False)
    with pytest.raises(RuntimeError, match='BLOCKED_EXTERNAL'):
        Pilot().poll()

def test_public_form_no_upload_fields():
    for file in Path('.github/ISSUE_TEMPLATE').glob('*.yml'):
        text = file.read_text()
        assert 'PUBLIC' in text
        assert 'id: contact_email' not in text and 'id: data_source' not in text

def test_orders_only_report_and_formula_safety(tmp_path):
    from openpyxl import load_workbook
    file = tmp_path/'orders.csv'
    file.write_bytes(CSV.replace(b'Test', b'=1+1'))
    result = IntelligencePipeline(str(file), output_dir=str(tmp_path/'out')).run()
    html = Path(result['deliverables']['html_dashboard']).read_text()
    assert 'N/A' in html and '100% 通过' not in html
    wb = load_workbook(result['deliverables']['excel_workbook'])
    assert not any(c.data_type == 'f' for s in wb for row in s for c in row)

def test_processing_crash_resumes():
    pilot = Pilot()
    job = ingest(pilot)
    pilot.state(job, 'PROCESSING')
    assert Pilot().process(job) == 'REVIEW_REQUIRED'

@pytest.mark.parametrize('payload', [
    CSV.replace(b'100,20', b'nan,20'), CSV.replace(b'100,20', b'100,'),
    CSV.replace(b'quantity,amount,', b'quantity,other,'),
    CSV.replace(b'2026-09-01', b'bad-date'), CSV.replace(b'Test,2', b'Test,-1'),
    CSV + CSV.splitlines()[1] + b'\n'])
def test_invalid_source_fails_before_delivery(payload):
    pilot = Pilot()
    job = ingest(pilot, payload=payload)
    assert pilot.process(job) == 'QA_FAILED'
    assert not (pilot.path(job)/'output/weekly_report.xlsx').exists()


def test_explicit_zero_cost_and_ads_are_known(tmp_path):
    from engine.models import CleanedAdRecord, InventoryItem
    file = tmp_path/'orders.csv'
    file.write_bytes(CSV.replace(b'100,20', b'100,0'))
    orders, _ = DataCleaner.clean_orders(str(file))
    ads = [CleanedAdRecord('2026-09-01','C','TEST','A',0,0,0,0,0)]
    summary = DataAnalyzer.analyze(orders, ads, {'A': InventoryItem('A','Test','Test',50,0,0,10)})
    assert summary.total_cogs == 0 and summary.total_ad_spend == 0
    assert summary.gross_profit == 100 and summary.gross_profit_margin_pct == 100
    assert summary.blended_roi is None  # Division by zero is not zero ROI.


def test_imap_simulated_receipt_readonly_dedup(monkeypatch):
    raw = mail()
    class IMAP:
        def __init__(self, *a): pass
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def login(self, *a): pass
        def select(self, folder, readonly):
            assert readonly is True
            return 'OK', []
        def response(self, key): return key, [b'123']
        def uid(self, action, *args):
            if action == 'search': return 'OK', [b'1 2']
            if args[-1] == '(RFC822.SIZE)': return 'OK', [b'1 (RFC822.SIZE 1000)']
            assert args[-1] == '(BODY.PEEK[])'
            return 'OK', [(b'1', raw)]
    monkeypatch.setattr('imaplib.IMAP4_SSL', IMAP)
    for key, value in {'PILOT_IMAP_HOST':'imap.example.com','PILOT_EMAIL':'test@example.com',
                       'PILOT_PASSWORD':'TEST','PILOT_ALLOWED_SENDERS':'buyer@example.com'}.items():
        monkeypatch.setenv(key, value)
    result = Pilot().poll()
    assert len(result) == 2 and result[0]['job'] == result[1]['job']
    assert all(r['state'] == 'REVIEW_REQUIRED' for r in result)
    assert Pilot().poll() == result


def test_smtp_connection_failure_safe_retry(monkeypatch):
    def fail(*args, **kwargs): raise ConnectionRefusedError()
    monkeypatch.setattr(smtplib, 'SMTP', fail)
    pilot, job = approved()
    assert pilot.send(job, CONFIG, ['buyer@example.com'])['state'] == 'SEND_FAILED'


def test_send_authorization_required():
    pilot, job = approved()
    with pytest.raises(ValueError):
        pilot.send(job, CONFIG, [])
    assert pilot.get(job)['state'] == 'APPROVED'


def test_html_source_text_escaped(tmp_path):
    file = tmp_path/'orders.csv'
    file.write_bytes(CSV.replace(b'Test', b'<script>alert(1)</script>'))
    result = IntelligencePipeline(str(file), output_dir=str(tmp_path/'out')).run()
    html = Path(result['deliverables']['html_dashboard']).read_text()
    assert '<script>alert(1)</script>' not in html
    assert '&lt;script&gt;' in html
