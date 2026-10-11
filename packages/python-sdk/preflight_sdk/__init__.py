"""Small synchronous Preflight client using opaque cookie sessions."""
import json
import urllib.request
import http.cookiejar


class Client:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.url = base_url.rstrip("/") + "/api/v1"
        self.csrf = ""
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))

    def request(self, method, path, data=None):
        request = urllib.request.Request(self.url + path, data=json.dumps(data).encode() if data is not None else None, method=method, headers={"Content-Type": "application/json", "X-CSRF-Token": self.csrf})
        with self.opener.open(request, timeout=30) as response:
            return json.load(response)

    def login(self, email, password):
        result = self.request("POST", "/auth/login", {"email": email, "password": password})
        self.csrf = result["csrf_token"]
        return result

    def register_agent(self, project_id, name, mode="accurate"):
        return self.request("POST", f"/projects/{project_id}/agents", {"name": name, "framework": "native", "version": "1.0.0", "config": {"mode": mode}})

    def evaluate(self, project_id, version_id, key, trials=1):
        return self.request("POST", f"/projects/{project_id}/runs", {"version_id": version_id, "idempotency_key": key, "trials": trials, "backend": "trusted-demo"})

    def run(self, run_id):
        return self.request("GET", f"/runs/{run_id}")
