"""
Unit test for DropWatcher.
"""
import os
import shutil
from engine.watcher import DropWatcher, INCOMING_DIR, PROCESSED_DIR, DELIVERABLES_ROOT

def test_drop_watcher(tmp_path, monkeypatch):
    import engine.watcher as watcher
    global INCOMING_DIR, PROCESSED_DIR, DELIVERABLES_ROOT
    INCOMING_DIR = str(tmp_path / "in")
    PROCESSED_DIR = str(tmp_path / "processed")
    DELIVERABLES_ROOT = str(tmp_path / "out")
    for name in ("INCOMING_DIR", "PROCESSED_DIR", "DELIVERABLES_ROOT"):
        monkeypatch.setattr(watcher, name, globals()[name])
    os.makedirs(INCOMING_DIR, exist_ok=True)
    test_file = os.path.join(INCOMING_DIR, "test_store_orders.csv")
    shutil.copy("tests/fixtures/orders_export.csv", test_file)

    results = DropWatcher.process_pending_drops()
    assert len(results) == 1
    assert results[0]["status"] == "SUCCESS"

    output_dir = os.path.dirname(results[0]["deliverables"]["html_dashboard"])
    assert os.path.exists(os.path.join(output_dir, "weekly_dashboard.html"))
    assert os.path.exists(os.path.join(output_dir, "weekly_report.xlsx"))
