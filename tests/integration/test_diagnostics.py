from preflight_eval import execute
from preflight_eval.diagnostics import trace_analysis, trace_diff
from preflight_security import Broker


def test_trace_graph_and_comparison():
    recovered = execute("tool-timeout")
    regressed = execute("tool-timeout", "regressed")
    graph = trace_analysis(recovered["events"])
    assert len(graph["edges"]) == len(graph["nodes"]) - 1
    assert graph["retry_count"] == 1
    assert graph["tool_errors"][0]["status"] == "timeout"
    assert not trace_diff(recovered["events"], regressed["events"])["equal_ignoring_timings"]
    assert trace_diff(recovered["events"], recovered["events"])["equal_ignoring_timings"]


def test_call_budget_and_loop_evidence():
    broker = Broker(max_calls=4)
    for i in range(6):
        broker.call("lookup", {})
    assert broker.events[-1]["status"] == "denied"
    assert trace_analysis([{**e, "sequence": i + 1} for i, e in enumerate(broker.events)])[
        "loop_suspected"
    ]
    broker.close()
