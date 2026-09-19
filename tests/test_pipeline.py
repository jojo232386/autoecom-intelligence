"""
Integration test for full IntelligencePipeline.
"""
import os
from engine.pipeline import IntelligencePipeline

def test_pipeline_execution(tmp_path):
    pipeline = IntelligencePipeline(
        orders_path="tests/fixtures/orders_export.csv",
        ads_path="tests/fixtures/ads_spend_export.csv",
        inventory_path="tests/fixtures/inventory_cost.csv",
        store_name="美澜风尚旗舰店",
        period_label="2026-W37周报",
        agency_name="代运营白牌数字化中心",
        output_dir=str(tmp_path)
    )
    result = pipeline.run(fail_on_audit=True)

    assert result["status"] == "SUCCESS"
    assert result["audit_passed"] is True

    for key, path in result["deliverables"].items():
        assert os.path.exists(path), f"File {path} does not exist"
        assert os.path.getsize(path) > 50, f"File {path} is empty or too small"
