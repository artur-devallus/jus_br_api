import abc
from abc import ABC
from typing import List

from bs4 import BeautifulSoup

from lib.exceptions import LibJusBrException
from lib.http_client import HttpClient
from lib.models import (
    SimpleProcessData,
    DetailedProcessData,
    CaseParty,
    Movement,
    Party, ProcessData, DocumentParty, AdditionalInfo
)
from lib.proxy import proxy_service
from lib.string_utils import only_digits


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

    @abc.abstractmethod
    def _extract_process_data(self, soup: BeautifulSoup) -> ProcessData:
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

    def _extract_additional_info(self, soup: BeautifulSoup) -> List[AdditionalInfo]:
        return []

    def close(self):
        self.http.close()

    @classmethod
    def _extract_document(cls, doc) -> DocumentParty | None:
        doc = str(doc).upper()
        only_digits_doc = only_digits(doc)
        if 'CNPJ' in str(doc) or '**************' in str(doc):
            return DocumentParty.of_cnpj(
                doc
                .replace('CNPJ', '')
                .replace('.', '')
                .replace('-', '')
                .replace(':', '')
                .replace('/', '')
                .replace('(', '')
                .replace(')', '')
                .strip()
            )
        elif 'CPF' in str(doc) or '**********' in str(doc):
            return DocumentParty.of_cpf(
                doc
                .replace('CPF', '')
                .replace('.', '')
                .replace('-', '')
                .replace(':', '')
                .replace('(', '')
                .replace(')', '')
                .strip()
            )
        elif 'OAB' in str(doc) or len(only_digits_doc) > 3:
            return DocumentParty.of_oab(doc.replace('OAB', '').strip())
        if len(only_digits_doc) > 1:
            raise LibJusBrException(f'cannot get document for {doc}')
        return DocumentParty.of_unknown(doc)
