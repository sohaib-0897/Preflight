import json
import sys
from preflight_eval.native import execute
request = json.loads(sys.stdin.read(16384))
print(json.dumps(execute(request["scenario_id"], request["mode"], request["seed"])))
