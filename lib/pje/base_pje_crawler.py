import warnings
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

from lib.exceptions import LibJusBrException
from lib.http_client import HttpClient
from lib.models import SimpleProcessData, DetailedProcessData, ProcessData, CaseParty, Movement

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)


class BasePjeCrawler(ABC):

    BASE_URL: str
    QUERY_PATH: str
    DETAIL_PATH: str
    SELECTORS: Dict[str, str]
    QUERY_FIELDS: Dict[str, Any]

    def __init__(self, proxy: Optional[str] = None, enable_logs: bool = False):
        self.http = HttpClient(self.BASE_URL, enable_logs=enable_logs)
        if proxy:
            self.http.session.proxies = {"https": proxy, "http": proxy}
        self._view_state = None
        self._initialize_session()

    # ==========================================================
    # Public API
    # ==========================================================

    def search(self, term: str) -> List[SimpleProcessData]:
        """Realiza uma busca pública e retorna uma lista de processos resumidos."""
        soup = self._query_soup(term)
        rows = soup.select(self.SELECTORS['table_rows'])
        return [self._parse_list_row(row) for row in rows]

    def detail(self, term: str) -> List[DetailedProcessData]:
        """Busca processos e retorna o detalhamento completo de cada um."""
        results = []
        for simple in self.search(term):
            url = self._build_detail_url(simple)
            results.append(self._extract_detail(url))
        return results

    # ==========================================================
    # Initialization flow
    # ==========================================================

    def _initialize_session(self):
        self.http.get("/")
        self.http.get("/pje/login.seam")
        self.http.get(self.QUERY_PATH)

    # ==========================================================
    # Query phase
    # ==========================================================

    def _query_soup(self, term: str) -> BeautifulSoup:
        """Executa a consulta pública e retorna o HTML parseado."""
        data = self._build_query_body(term)
        headers = self._build_default_headers()
        url = urljoin(self.BASE_URL, self.QUERY_PATH)
        r = self.http.post(url, data=data, headers=headers)

        soup = BeautifulSoup(r.text, "html.parser")
        table_div = soup.select_one(self.SELECTORS["table_container"])
        if not table_div:
            raise LibJusBrException("Tabela de processos não encontrada na resposta HTML.")
        return table_div

    def _build_default_headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": self.BASE_URL,
            "Referer": urljoin(self.BASE_URL, self.QUERY_PATH),
        }

    @abstractmethod
    def _build_query_body(self, term: str) -> Dict[str, Any]:
        """Retorna o corpo da requisição POST do tribunal (ViewState + parâmetros)."""
        ...

    @abstractmethod
    def _parse_list_row(self, row) -> SimpleProcessData:
        """Transforma uma linha da tabela em um SimpleProcessData."""
        ...

    @abstractmethod
    def _build_detail_url(self, simple: SimpleProcessData) -> str:
        """Monta a URL de detalhe do processo."""
        ...

    # ==========================================================
    # Detail extraction
    # ==========================================================

    def _extract_detail(self, url: str) -> DetailedProcessData:
        """Carrega e parseia os detalhes de um processo."""
        r = self.http.get(url)
        soup = BeautifulSoup(r.text, "html.parser")

        return DetailedProcessData(
            process=self._extract_process_data(soup),
            case_parties=self._extract_case_parties(soup),
            movements=self._extract_movements(soup),
        )

    @abstractmethod
    def _extract_process_data(self, soup: BeautifulSoup) -> ProcessData:
        ...

    @abstractmethod
    def _extract_case_parties(self, soup: BeautifulSoup) -> CaseParty:
        ...

    @abstractmethod
    def _extract_movements(self, soup: BeautifulSoup) -> List[Movement]:
        ...

    def close(self):
        """Fecha a sessão HTTP."""
        self.http.close()
