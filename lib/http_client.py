from urllib.parse import urlparse

import httpx
from tenacity import retry, wait_exponential, retry_if_exception_type, retry_if_exception

FORBIDDEN_CODE = 403
_retry_forbidden = retry_if_exception(
    lambda ex: isinstance(ex, httpx.HTTPStatusError) and ex.response.status_code == FORBIDDEN_CODE
)

_retry = (
        _retry_forbidden |
        retry_if_exception_type(httpx.ReadError) |
        retry_if_exception_type(httpx.ConnectError)
)


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
                request=[self._add_headers, self.log_request],
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
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Connection": "keep-alive",
                'Upgrade-Insecure-Requests': '1',
            },
        )

    @retry(wait=wait_exponential(multiplier=0.5, max=3), retry=_retry)
    def get(self, url: str, **kwargs) -> httpx.Response:
        res = self.session.get(url, **kwargs)
        if res.is_error:
            res.raise_for_status()
        return res

    @retry(wait=wait_exponential(multiplier=0.5, max=3), retry=_retry)
    def post(self, url: str, data: dict | str | None = None, **kwargs) -> httpx.Response:
        res = self.session.post(url, data=data, **kwargs)
        if res.is_error:
            res.raise_for_status()
        return res

    def close(self):
        self.session.close()

    @classmethod
    def _add_headers(cls, request: httpx.Request) -> None:
        request.headers['Host'] = str(urlparse(str(request.url)).netloc)
        request.headers['cache-control'] = 'no-cache'
        request.headers['dnt'] = '1'
        request.headers['pragma'] = 'no-cache'
        request.headers['priority'] = 'u=0, i'
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

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
