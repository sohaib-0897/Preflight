import hashlib
import json
from collections import Counter


def trace_analysis(events):
    calls = [e for e in events if e.get("kind") == "tool_call"]
    signatures = [json.dumps([e.get("tool"), e.get("arguments")], sort_keys=True) for e in calls]
    counts = Counter(signatures)
    return {"nodes": [{"id": e["sequence"], "kind": e["kind"], "tool": e.get("tool"), "status": e.get("status")} for e in events], "edges": [{"source": e.get("parent",0), "target": e["sequence"]} for e in events if e["sequence"] != 0], "duplicate_calls": [{"signature_sha256": hashlib.sha256(k.encode()).hexdigest(), "count": v} for k,v in counts.items() if v>1], "loop_suspected": max(counts.values(),default=0)>4, "tool_errors": [{"sequence": e["sequence"], "tool": e.get("tool"), "status": e.get("status")} for e in calls if e.get("status") != "ok"], "retry_count": sum(max(0,n-1) for n in counts.values()), "limitations": "Duplicate calls may be valid retries. Loop classification is a deterministic heuristic."}


def trace_diff(left, right):
    def canonical(events):
        return [{k:e[k] for k in ["kind","tool","arguments","result","status","output"] if k in e} for e in events]
    l, r = canonical(left), canonical(right)
    return {"equal_ignoring_timings": l==r, "baseline_steps": len(l), "candidate_steps": len(r), "differences": [{"step": i, "baseline": l[i] if i<len(l) else None, "candidate": r[i] if i<len(r) else None} for i in range(max(len(l),len(r))) if (l[i] if i<len(l) else None)!=(r[i] if i<len(r) else None)]}
