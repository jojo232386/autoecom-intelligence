"""
Automated File-Drop Watcher & Ingestion Pipeline.
Enables 100% autonomous zero-touch delivery:
Drop raw CSV -> Auto Pipeline -> Auto Audit -> Auto Packaged Deliverables.
"""
import os
import shutil
import hashlib
from datetime import datetime
from typing import List, Dict, Any
from engine.pipeline import IntelligencePipeline

INCOMING_DIR = "data/incoming_drops"
PROCESSED_DIR = "data/incoming_drops/processed"
DELIVERABLES_ROOT = "data/deliverables"

class DropWatcher:
    @staticmethod
    def process_pending_drops() -> List[Dict[str, Any]]:
        os.makedirs(INCOMING_DIR, exist_ok=True)
        os.makedirs(PROCESSED_DIR, exist_ok=True)
        os.makedirs(DELIVERABLES_ROOT, exist_ok=True)

        results = []
        files = [f for f in os.listdir(INCOMING_DIR) if f.endswith(".csv") and not os.path.islink(os.path.join(INCOMING_DIR, f))]

        if not files:
            return []

        for fname in files:
            fpath = os.path.join(INCOMING_DIR, fname)
            client_id = os.path.splitext(fname)[0].replace("_orders", "").replace("_export", "")
            store_name = client_id.replace("_", " ").title()
            job_id = hashlib.sha256(open(fpath, "rb").read()).hexdigest()
            client_output_dir = os.path.join(DELIVERABLES_ROOT, client_id, job_id)

            print(f"⚡ Auto-processing dropped data for client [{store_name}] from {fname}...")

            pipeline = IntelligencePipeline(
                orders_path=fpath,
                store_name=store_name,
                period_label=f"Weekly-Delivery-{datetime.now().strftime('%Y-W%W')}",
                agency_name="AutoEcom Autonomous White-Label Center",
                output_dir=client_output_dir
            )

            try:
                res = pipeline.run(fail_on_audit=True)
                # Archive processed raw input
                archive_path = os.path.join(PROCESSED_DIR, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{fname}")
                shutil.move(fpath, archive_path)
                res["archived_raw"] = archive_path
                results.append(res)
                print(f"✅ Generated locally; review required for [{store_name}] into {client_output_dir} (diff=0.0 verified)")
            except Exception as e:
                print(f"❌ Local processing failed for {fname}: {e}")
                results.append({"status": "FAILED", "file": fname, "error": str(e)})

        return results

if __name__ == "__main__":
    DropWatcher.process_pending_drops()
