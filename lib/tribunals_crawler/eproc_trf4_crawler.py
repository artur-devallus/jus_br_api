from typing import List

from bs4 import BeautifulSoup

from lib.models import Movement, ProcessData, Party, DetailedProcessData, SimpleProcessData
from lib.tribunals_crawler.abstract_crawler import AbstractCrawler


class Trf4Crawler(AbstractCrawler):
    def query_process_list(self, term: str) -> List[SimpleProcessData]:
        pass

    def detail_process_list(self, term: str) -> List[DetailedProcessData]:
        pass

    def _init_session(self):
        pass

    def _extract_active_party(self, soup: BeautifulSoup, url: str) -> List[Party]:
        pass

    def _extract_passive_party(self, soup: BeautifulSoup, url: str) -> List[Party]:
        pass

    def _extract_other_party(self, soup: BeautifulSoup, url: str) -> List[Party]:
        pass

    def _extract_process_data(self, soup: BeautifulSoup) -> ProcessData:
        pass

    def _extract_movements(self, soup: BeautifulSoup, url) -> List[Movement]:
        pass