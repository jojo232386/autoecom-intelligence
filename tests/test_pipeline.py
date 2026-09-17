"""
Integration test for full IntelligencePipeline.
"""
import os
from engine.pipeline import IntelligencePipeline

def test_pipeline_execution():
    pipeline = IntelligencePipeline(
        orders_path="data/raw_inputs/orders_export.csv",
        ads_path="data/raw_inputs/ads_spend_export.csv",
        inventory_path="data/raw_inputs/inventory_cost.csv",
        store_name="美澜风尚旗舰店",
        period_label="2026-W37周报",
        agency_name="代运营白牌数字化中心",
        output_dir="data/deliverables"
    )
    result = pipeline.run(fail_on_audit=True)

    assert result["status"] == "SUCCESS"
    assert result["audit_passed"] is True

    for key, path in result["deliverables"].items():
        assert os.path.exists(path), f"File {path} does not exist"
        assert os.path.getsize(path) > 50, f"File {path} is empty or too small"
