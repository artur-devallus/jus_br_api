import httpx


class HttpClient:
    def __init__(self, base_url: str | None = None, timeout: int = 60, enable_logs: bool = False):
        self.base_url = base_url.rstrip("/") if base_url else None
        self.enable_logs = enable_logs
        self.session: httpx.Client = httpx.Client(
            base_url=self.base_url,
            follow_redirects=True,
            timeout=timeout,
            event_hooks=dict(
                request=[self.log_request],
            ),
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/141.0.0.0 Mobile Safari/537.36"
                ),
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "DNT": "1",
                "Pragma": "no-cache",
            },
        )

    def get(self, url: str, **kwargs) -> httpx.Response:
        return self.session.get(url, **kwargs)

    def post(self, url: str, data: dict | str | None = None, **kwargs) -> httpx.Response:
        return self.session.post(url, data=data, **kwargs)

    def close(self):
        self.session.close()

    def log_request(self, request: httpx.Request) -> None:
        if not self.enable_logs:
            return
        print(request.url)
        print(request.headers)
