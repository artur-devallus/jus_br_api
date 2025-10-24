import abc
from abc import ABC
from typing import List

from bs4 import BeautifulSoup

from lib.http_client import HttpClient
from lib.models import (
    SimpleProcessData,
    DetailedProcessData,
    CaseParty,
    Movement,
    Party
)
from lib.proxy import proxy_service


class AbstractCrawler(ABC):
    BASE_URL: str

    def __init__(self, use_proxy: bool = False):
        if use_proxy:
            proxy = proxy_service.get_fastest_proxy(self.BASE_URL)
        else:
            proxy = None
        self.http = HttpClient(
            self.BASE_URL,
            proxy=proxy
        )
        self._init_session()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @abc.abstractmethod
    def query_process_list(self, term: str) -> List[SimpleProcessData]:
        ...

    @abc.abstractmethod
    def detail_process_list(self, term: str) -> List[DetailedProcessData]:
        ...

    @abc.abstractmethod
    def _init_session(self):
        ...

    @abc.abstractmethod
    def _extract_active_party(self, soup: BeautifulSoup, url: str) -> List[Party]:
        ...

    @abc.abstractmethod
    def _extract_passive_party(self, soup: BeautifulSoup, url: str) -> List[Party]:
        ...

    @abc.abstractmethod
    def _extract_other_party(self, soup: BeautifulSoup, url: str) -> List[Party]:
        ...

    def _extract_case_parties(self, soup: BeautifulSoup, url) -> CaseParty:
        active = self._extract_active_party(soup, url)
        assert len(active) > 0
        passive = self._extract_passive_party(soup, url)
        assert len(passive) > 0
        return CaseParty(
            active=active,
            passive=passive,
            others=self._extract_other_party(soup, url),
        )

    @abc.abstractmethod
    def _extract_movements(self, soup: BeautifulSoup, url) -> List[Movement]:
        ...

    def close(self):
        self.http.close()
