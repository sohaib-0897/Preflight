from preflight_eval import execute
from preflight_scoring import aggregate


def test_measured_latency_and_unknown_cost():
    fast = execute("latency", "accurate")
    slow = execute("latency", "slow")
    assert slow["latency_ms"] >= 20
    assert slow["latency_ms"] > fast["latency_ms"]
    assert slow["tool_calls"] > fast["tool_calls"]
    summary = aggregate([fast, slow])
    assert summary["token_usage"] is None and summary["estimated_cost"] is None
    assert summary["sample_size"] == 2 and summary["effective_sample_size"] == 1
