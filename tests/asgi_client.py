"""Real ASGI transport without TestClient's cross-thread socket wakeups."""

import asyncio
import httpx


class ASGIClient:
    __test__ = False

    def __init__(self, app):
        self.app = app
        self.headers = {}
        self.cookies = httpx.Cookies()

    def __enter__(self):
        self.app.state.db.initialize()
        return self

    def __exit__(self, *args):
        pass

    def request(self, method, path, **kwargs):
        async def send():
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=self.app),
                base_url="http://testserver",
                headers=self.headers,
                cookies=self.cookies,
            ) as client:
                result = await client.request(method, path, **kwargs)
                self.cookies = client.cookies
                return result

        return asyncio.run(send())

    def get(self, path, **kwargs):
        return self.request("GET", path, **kwargs)

    def post(self, path, **kwargs):
        return self.request("POST", path, **kwargs)
