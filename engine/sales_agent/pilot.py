"""Private, review-gated one-store CSV pilot using the existing CRM and pipeline."""
import hashlib
import fcntl
import imaplib
import json
import os
from email import policy
from email.parser import BytesParser
from email.message import EmailMessage
from email.utils import parseaddr
from pathlib import Path

from engine.pipeline import IntelligencePipeline
from engine.sales_agent import crm
from engine.sales_agent.dispatcher import OutreachDispatcher

MAX_BYTES = 5_000_000


def digest(data):
    return hashlib.sha256(data).hexdigest()


class Pilot:
    def __init__(self):
        crm.init_crm_db()
        self.root = Path(crm.DB_PATH).resolve().parent / 'jobs'
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        with crm.get_db_connection() as db:
            db.executescript('''
            CREATE TABLE IF NOT EXISTS pilot_jobs (
                id TEXT PRIMARY KEY, customer TEXT NOT NULL, provider_id TEXT NOT NULL,
                state TEXT NOT NULL, attempts INTEGER NOT NULL DEFAULT 0,
                manifest TEXT, reviewer TEXT, evidence TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS suppression (customer TEXT PRIMARY KEY);
            ''')

    def get(self, job):
        with crm.get_db_connection() as db:
            row = db.execute('SELECT * FROM pilot_jobs WHERE id=?', (job,)).fetchone()
        if row is None:
            raise ValueError('Unknown job')
        return dict(row)

    def path(self, job):
        row = self.get(job)
        return self.root / digest(row['customer'].encode()) / job

    def state(self, job, state, evidence=None):
        with crm.get_db_connection() as db:
            db.execute('UPDATE pilot_jobs SET state=?, evidence=?, updated_at=CURRENT_TIMESTAMP WHERE id=?',
                       (state, json.dumps(evidence), job))

    def suppressed(self, customer):
        with crm.get_db_connection() as db:
            return db.execute('SELECT 1 FROM suppression WHERE customer=?', (customer,)).fetchone() is not None

    def ingest(self, raw, provider_id, allowed_senders):
        if len(raw) > MAX_BYTES:
            raise ValueError('Message too large')
        msg = BytesParser(policy=policy.default).parsebytes(raw)
        addresses = msg.get_all('From', [])
        customer = parseaddr(str(addresses[0]))[1].lower() if len(addresses) == 1 else ''
        if customer not in {s.lower() for s in allowed_senders} or '@' not in customer:
            raise ValueError('Sender not authorized for this private pilot')
        body = msg.get_body(preferencelist=('plain',))
        text = body.get_content().strip().lower() if body else ''
        subject = str(msg.get('Subject', '')).strip().lower()
        if subject in ('unsubscribe', 'stop', '退订', '拒绝联系') or text in ('unsubscribe', 'stop', '退订', '拒绝联系'):
            with crm.get_db_connection() as db:
                db.execute('INSERT OR IGNORE INTO suppression VALUES (?)', (customer,))
            return 'SUPPRESSED'
        if self.suppressed(customer):
            return 'SUPPRESSED'
        attachments = {}
        for part in msg.iter_attachments():
            name = part.get_filename()
            if name not in {'orders.csv', 'ads.csv', 'inventory.csv'} or name in attachments:
                raise ValueError('Only unique orders.csv, ads.csv, inventory.csv allowed')
            payload = part.get_payload(decode=True)
            if not payload or len(payload) > MAX_BYTES:
                raise ValueError('Invalid attachment')
            payload.decode('utf-8-sig')
            attachments[name] = payload
        if 'orders.csv' not in attachments:
            raise ValueError('orders.csv required; no link downloads')
        # Deduplicate a resent payload even with a changed Message-ID/IMAP UID.
        identity = json.dumps([customer, [(n, digest(attachments[n])) for n in sorted(attachments)]], separators=(',', ':')).encode()
        job = digest(identity)
        with crm.get_db_connection() as db:
            db.execute('INSERT OR IGNORE INTO pilot_jobs(id,customer,provider_id,state) VALUES (?,?,?,?)',
                       (job, customer, str(provider_id), 'RECEIVING'))
        if self.get(job)['state'] != 'RECEIVING':
            return job
        folder = self.path(job)
        folder.mkdir(parents=True, exist_ok=True, mode=0o700)
        for name, data in attachments.items():
            path = folder / name
            path.write_bytes(data)
            path.chmod(0o600)
        self.state(job, 'RECEIVED', {'provider_id': str(provider_id), 'payload_sha256': job})
        return job

    def process(self, job):
        # OS lock releases on crash; deterministic local processing is safe to resume.
        with (self.path(job) / '.process.lock').open('a') as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                return 'PROCESSING'
            return self._process(job)

    def _process(self, job):
        with crm.get_db_connection() as db:
            changed = db.execute("UPDATE pilot_jobs SET state='PROCESSING' WHERE id=? AND state IN ('RECEIVED','PROCESSING')", (job,)).rowcount
        if not changed:
            return self.get(job)['state']
        folder = self.path(job)
        try:
            result = IntelligencePipeline(str(folder / 'orders.csv'),
                str(folder / 'ads.csv') if (folder / 'ads.csv').exists() else None,
                str(folder / 'inventory.csv') if (folder / 'inventory.csv').exists() else None,
                store_name='Private pilot', period_label='Source data period', output_dir=str(folder / 'output')).run()
            if not result['audit_passed']:
                raise ValueError('Audit failed')
            manifest = {Path(p).name: digest(Path(p).read_bytes()) for p in result['deliverables'].values()}
            with crm.get_db_connection() as db:
                db.execute("UPDATE pilot_jobs SET state='REVIEW_REQUIRED',manifest=? WHERE id=?", (json.dumps(manifest, sort_keys=True), job))
        except Exception as exc:
            self.state(job, 'QA_FAILED', {'error_type': type(exc).__name__})
        return self.get(job)['state']

    def approve(self, job, manifest_hash, reviewer):
        row = self.get(job)
        if row['state'] != 'REVIEW_REQUIRED' or not reviewer.strip() or digest(row['manifest'].encode()) != manifest_hash:
            raise ValueError('Review must identify reviewer and exact manifest hash')
        self.verify_files(job)
        with crm.get_db_connection() as db:
            db.execute("UPDATE pilot_jobs SET state='APPROVED',reviewer=? WHERE id=? AND state='REVIEW_REQUIRED'", (reviewer, job))

    def verify_files(self, job):
        row = self.get(job)
        manifest = json.loads(row['manifest'] or '{}')
        if not manifest:
            raise ValueError('Missing manifest')
        for name, expected in manifest.items():
            if Path(name).name != name or digest((self.path(job) / 'output' / name).read_bytes()) != expected:
                raise ValueError('Artifact changed after review')
        return manifest

    def send(self, job, config, authorized_recipients):
        row = self.get(job)
        if row['customer'] not in authorized_recipients or self.suppressed(row['customer']):
            raise ValueError('Recipient not authorized or suppressed')
        manifest = self.verify_files(job)
        msg = EmailMessage()
        msg['From'] = config['sender_email']
        msg['To'] = row['customer']
        msg['Subject'] = 'Requested CSV pilot report'
        msg['Message-ID'] = f'<{job}@{config["sender_email"].split("@")[-1]}>'
        msg.set_content('Your reviewed pilot report is attached. N/A means the source data or accounting rules were insufficient. Reply STOP to opt out. This is not confirmation of payment or acceptance.')
        for name in manifest:
            msg.add_attachment((self.path(job) / 'output' / name).read_bytes(), maintype='application', subtype='octet-stream', filename=name)
        with crm.get_db_connection() as db:
            changed = db.execute("UPDATE pilot_jobs SET state='SENDING',attempts=attempts+1 WHERE id=? AND state IN ('APPROVED','SEND_FAILED') AND attempts<3 AND customer NOT IN (SELECT customer FROM suppression)", (job,)).rowcount
        if not changed:
            raise ValueError('Not approved, attempts exhausted, or send needs reconciliation')
        # A process crash in SENDING remains blocked; never retry ambiguous sends.
        result = OutreachDispatcher.send_message_smtp(msg, **config)
        self.state(job, result['state'], result)
        return result

    def poll(self):
        required = ('PILOT_IMAP_HOST', 'PILOT_EMAIL', 'PILOT_PASSWORD', 'PILOT_ALLOWED_SENDERS')
        if not all(os.getenv(key) for key in required):
            raise RuntimeError('BLOCKED_EXTERNAL: private mailbox not configured')
        results = []
        with imaplib.IMAP4_SSL(os.environ['PILOT_IMAP_HOST']) as mailbox:
            mailbox.login(os.environ['PILOT_EMAIL'], os.environ['PILOT_PASSWORD'])
            status, _ = mailbox.select('INBOX', readonly=True)
            if status != 'OK':
                raise RuntimeError('Mailbox selection failed')
            validity = mailbox.response('UIDVALIDITY')[1]
            status, uids = mailbox.uid('search', None, 'ALL')
            if status != 'OK':
                raise RuntimeError('Mailbox search failed')
            for uid in uids[0].split()[-100:]:
                status, data = mailbox.uid('fetch', uid, '(RFC822.SIZE)')
                import re
                sizes = re.findall(rb'RFC822.SIZE (\d+)', b' '.join(d for d in data if isinstance(d, bytes)))
                if status != 'OK' or not sizes or int(sizes[0]) > MAX_BYTES:
                    continue
                status, data = mailbox.uid('fetch', uid, '(BODY.PEEK[])')
                if status != 'OK':
                    continue
                for item in data:
                    if isinstance(item, tuple):
                        try:
                            job = self.ingest(item[1], f'{validity}:{uid.decode()}', os.environ['PILOT_ALLOWED_SENDERS'].split(','))
                            results.append({'job': job, 'state': self.process(job) if job != 'SUPPRESSED' else job})
                        except (ValueError, UnicodeError):
                            results.append({'state': 'REJECTED_INPUT', 'uid': uid.decode()})
        return results
