"""
Unit test for Workflow Automation PoW adapter.
"""
from business.proof_of_work.workflow_pipeline_pow import run_proof_demo

def test_workflow_pow_execution():
    assert run_proof_demo() is True
