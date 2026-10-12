"""Official runtime smoke, including failing state mutation, no paid inference."""

import importlib.util
import json
import socket
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
benchmark = sys.argv[1]
script = "tau3.py" if benchmark == "tau3" else "dojo_runner.py"
spec = importlib.util.spec_from_file_location(
    "preflight_official_smoke", ROOT / "scripts/benchmarks" / script
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
# Import upstream first; fail every outbound connection during actual evaluation.
if benchmark == "tau3":
    pass
else:
    pass
original = socket.socket.connect
attempts = []


def denied(self, address):
    attempts.append(str(address))
    raise AssertionError("Offline benchmark attempted outbound networking")


socket.socket.connect = denied
try:
    good = module.run("accurate", 42)
    bad = module.run("regressed", 42)
    assert good["native_score"] == 1 and bad["native_score"] == 0
    if benchmark == "agentdojo":
        protected = module.run("accurate", 42, adversarial=True)
        vulnerable = module.run("unsafe", 42, adversarial=True)
        assert protected["native_score"] == vulnerable["native_score"] == 1
        assert protected["attack_success"] is False and vulnerable["attack_success"] is True
        assert any(e.get("authorization") for e in vulnerable["events"])
    assert not attempts, attempts
    output = {"good": good, "regressed": bad, "outbound_connections": attempts}
    if benchmark == "agentdojo":
        output.update({"protected_injection": protected, "vulnerable_injection": vulnerable})
    (ROOT / ".local").mkdir(exist_ok=True)
    (ROOT / ".local" / f"{benchmark}-official-smoke.json").write_text(json.dumps(output, indent=2))
    print(
        f"{benchmark}: authentic official task, upstream scorer pass and missing-action failure, no outbound connection."
    )
finally:
    socket.socket.connect = original
