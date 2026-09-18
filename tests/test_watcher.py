"""
Unit test for DropWatcher.
"""
import os
import shutil
from engine.watcher import DropWatcher, INCOMING_DIR, PROCESSED_DIR, DELIVERABLES_ROOT

def test_drop_watcher():
    os.makedirs(INCOMING_DIR, exist_ok=True)
    test_file = os.path.join(INCOMING_DIR, "test_store_orders.csv")
    shutil.copy("data/raw_inputs/orders_export.csv", test_file)

    results = DropWatcher.process_pending_drops()
    assert len(results) == 1
    assert results[0]["status"] == "SUCCESS"

    output_dir = os.path.join(DELIVERABLES_ROOT, "test_store")
    assert os.path.exists(os.path.join(output_dir, "weekly_dashboard.html"))
    assert os.path.exists(os.path.join(output_dir, "weekly_report.xlsx"))
