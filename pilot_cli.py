"""Private pilot operator CLI. No transmission without explicit recipient scope."""
import argparse
import json
import os
from engine.sales_agent.pilot import Pilot, digest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['poll', 'status', 'process', 'approve', 'send'])
    parser.add_argument('--job')
    parser.add_argument('--manifest-hash')
    parser.add_argument('--reviewer')
    args = parser.parse_args()
    pilot = Pilot()
    if args.action == 'poll':
        print(json.dumps(pilot.poll()))
        return
    if not args.job:
        parser.error('--job required')
    if args.action == 'status':
        row = pilot.get(args.job)
        row['manifest_hash'] = digest((row['manifest'] or '').encode())
        print(json.dumps(row, indent=2))
    elif args.action == 'process':
        print(pilot.process(args.job))
    elif args.action == 'approve':
        pilot.approve(args.job, args.manifest_hash or '', args.reviewer or '')
    elif args.action == 'send':
        required = ['PILOT_SMTP_HOST', 'PILOT_EMAIL', 'PILOT_PASSWORD', 'PILOT_SEND_AUTHORIZED']
        if not all(os.getenv(k) for k in required):
            raise RuntimeError('BLOCKED_EXTERNAL: sender credentials and recipient authorization required')
        print(pilot.send(args.job, dict(smtp_host=os.environ['PILOT_SMTP_HOST'],
            smtp_port=int(os.getenv('PILOT_SMTP_PORT', '587')), sender_email=os.environ['PILOT_EMAIL'],
            sender_password=os.environ['PILOT_PASSWORD']), os.environ['PILOT_SEND_AUTHORIZED'].split(',')))


if __name__ == '__main__':
    main()
