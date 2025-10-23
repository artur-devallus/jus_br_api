from urllib.parse import urlparse

import httpx


class HttpClient:
    def __init__(
            self, base_url: str | None = None,
            timeout: float = 30,
            enable_logs: bool = False,
            proxy: str = None
    ):
        self.base_url = base_url.rstrip("/") if base_url else None
        self.enable_logs = enable_logs
        self.session: httpx.Client = httpx.Client(
            base_url=self.base_url,
            follow_redirects=True,
            timeout=timeout,
            event_hooks=dict(
                request=[self.add_host, self.log_request],
            ),
            mounts={
                'http://': httpx.HTTPTransport(proxy=proxy),
                'https://': httpx.HTTPTransport(proxy=proxy),
            } if proxy else None,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (X11; Linux x86_64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/141.0.0.0 Safari/537.36"
                ),
                "Accept": "*",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Connection": "keep-alive",
                'Upgrade-Insecure-Requests': '1',
            },
        )

    def get(self, url: str, **kwargs) -> httpx.Response:
        last_ex = None
        for i in range(3):
            try:
                return self.session.get(url, **kwargs)
            except httpx.ReadError as ex:
                last_ex = ex
        raise last_ex

    def post(self, url: str, data: dict | str | None = None, **kwargs) -> httpx.Response:
        res = self.session.post(url, data=data, **kwargs)
        if res.is_error:
            print(url)
            print(data)
            print(kwargs)
            res.raise_for_status()
        return res

    def close(self):
        self.session.close()

    @classmethod
    def add_host(cls, request: httpx.Request) -> None:
        request.headers['Host'] = str(urlparse(str(request.url)).netloc)
        request.headers['sec-ch-ua'] = '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"'
        request.headers['sec-ch-ua-mobile'] = '?0'
        request.headers['sec-ch-ua-platform'] = 'Linux'
        request.headers['sec-fetch-dest'] = 'document'
        request.headers['sec-fetch-mode'] = 'navigate'
        request.headers['sec-fetch-site'] = 'none'
        request.headers['sec-fetch-user'] = '?1'

    def log_request(self, request: httpx.Request) -> None:
        if not self.enable_logs:
            return
        print(request.url)
        print(request.headers)
