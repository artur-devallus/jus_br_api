from concurrent.futures import ThreadPoolExecutor, as_completed
from time import perf_counter
from typing import List, Optional, Tuple

from lib.http_client import HttpClient
from lib.log_utils import get_logger

logger = get_logger("dynamic_proxy_service")


class DynamicProxyService:
    PROXY_URL = 'https://api.proxyscrape.com'
    PROXY_SOURCE_PATH = '/v4/free-proxy-list/get'
    PROXY_SOURCE_PARAMS = dict(
        request='display_proxies',
        country='br',
        proxy_format='protocolipport',
        format='json',
        timeout='4000'
    )

    def __init__(self,
                 timeout: float = 3.0,
                 max_workers: int = 30,
                 enable_logs: bool = False):
        self.timeout = timeout
        self.max_workers = max_workers
        self.enable_logs = enable_logs
        self.proxies = self._fetch_proxies()

    # -------------------------------------------------------------------------
    # PUBLIC API
    # -------------------------------------------------------------------------
    def get_fastest_proxy(self, for_url: str) -> Optional[str]:
        """
        Obtém proxies da API pública e retorna o mais rápido que responde com HTTP 200.
        """
        logger.info("Obtendo lista de proxies da API pública...")

        if not self.proxies:
            logger.warning("Nenhum proxy válido encontrado na API.")
            return None

        logger.info(f"Total de proxies recebidos: {len(self.proxies)}")
        fastest = self._find_fastest_proxy(self.proxies, for_url)

        if fastest:
            logger.info(f"Proxy mais rápido: {fastest}")
        else:
            logger.warning("Nenhum proxy funcional encontrado.")

        return fastest

    # -------------------------------------------------------------------------
    # PRIVATE HELPERS
    # -------------------------------------------------------------------------
    def _fetch_proxies(self) -> List[str]:
        """
        Faz requisição à API do ProxyScrape e retorna uma lista de URLs de proxy.
        """
        try:
            with HttpClient(
                    base_url=self.PROXY_URL,
                    timeout=self.timeout,
                    enable_logs=self.enable_logs
            ) as client:
                response = client.get(
                    self.PROXY_SOURCE_PATH,
                    params=self.PROXY_SOURCE_PARAMS
                )

            if response.is_error:
                logger.error(f'Erro ao buscar proxies: {response.status_code}')
                return []

            data = response.json()
            proxies = [
                p['proxy']
                for p in data.get('proxies', [])
                if p.get('alive') and p.get('proxy')
            ]

            return proxies

        except Exception as ex:
            logger.exception(f"Erro inesperado ao buscar proxies: {ex}")
            return []

    def _find_fastest_proxy(self, proxies: List[str], test_url: str) -> Optional[str]:
        """
        Testa todos os proxies em paralelo e retorna o mais rápido com status 200.
        """
        results: List[Tuple[str, float, int]] = []
        workers = min(self.max_workers, len(proxies))

        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(self._probe_proxy, p, test_url): p for p in proxies
            }

            for fut in as_completed(futures):
                result = fut.result()
                if result and result[2] == 200:
                    results.append(result)

        if not results:
            return None

        # Ordena por tempo de resposta (menor é melhor)
        results.sort(key=lambda x: x[1])
        return results[0][0]

    def _probe_proxy(self, proxy: str, test_url) -> Optional[Tuple[str, float, int]]:
        """
        Realiza um teste individual de proxy e retorna:
        (proxy, tempo_resposta, status_code)
        """
        try:
            with HttpClient(
                    base_url=self.PROXY_URL,
                    timeout=self.timeout,
                    proxy=proxy,
                    enable_logs=self.enable_logs
            ) as client:
                start = perf_counter()
                response = client.get(test_url)
                elapsed = perf_counter() - start
                return proxy, elapsed, response.status_code

        except Exception as ex:
            if self.enable_logs:
                logger.debug(f"Proxy {proxy} falhou: {ex}")
            return None


proxy_service = DynamicProxyService()
