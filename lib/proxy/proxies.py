import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import perf_counter
from typing import List, Optional, Tuple

from lib.http_client import HttpClient

logger = logging.getLogger('bradesco_proxy')


def _probe_proxy(proxy: str, url: str, timeout: float) -> Optional[Tuple[str, float, int]]:
    client = None
    try:
        client = HttpClient(base_url=url, proxy=proxy, timeout=timeout)

        start = perf_counter()
        r = client.get('', follow_redirects=True)
        elapsed = perf_counter() - start
        return proxy, elapsed, r.status_code
    except (RuntimeError, Exception) as ex:
        return None
    finally:
        if client:
            client.close()


def fastest_proxy(url: str,
                  timeout: float = 3.0,
                  max_workers: int = 30) -> Optional[str]:
    with open("/home/artur/Documents/Projects/Python/jus-br-lib/lib/proxy/proxies.txt", "r", encoding="utf-8") as f:
        proxies = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
    if not proxies:
        return None

    candidates = [p.strip() for p in proxies if p and ":" in p]
    if not candidates:
        return None

    results: List[Tuple[str, float, int]] = []
    workers = min(max_workers, len(candidates))

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(_probe_proxy, p, url, timeout): p for p in candidates}
        for fut in as_completed(futures):
            res = fut.result()
            if res and res[2] == 200:
                results.append(res)

    if not results:
        return None

    results.sort(key=lambda x: x[1])

    fastest = results[0]
    print(f'fastest proxy {fastest[0]} with {fastest[1]} seconds')
    return fastest[0]


if __name__ == '__main__':
    print(fastest_proxy())
