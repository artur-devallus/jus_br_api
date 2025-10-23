from typing import List

from bs4 import BeautifulSoup

from lib.json_utils import json_dump
from lib.models import Party
from lib.pje.base_pje_crawler import BasePjeCrawler


class _PjeTrf5Crawler(BasePjeCrawler):
    QUERY_PATH = "/pjeconsulta/ConsultaPublica/listView.seam"
    DETAIL_PATH = "/pjeconsulta/ConsultaPublica/DetalheProcessoConsultaPublica/listView.seam"

    ACTIVE_PARTY_BINDING = 'j_id140:processoPartesPoloAtivoResumidoList:j_id327'
    PASSIVE_PARTY_BINDING = 'j_id140:processoPartesPoloPassivoResumidoList:j_id391'

    MOVEMENT_AJAX_REQUEST = 'j_id140:j_id464'
    MOVEMENT_AJAX_BINDING = 'j_id140:j_id545'

    def _build_query_body(self, term):
        body = super()._build_query_body(term)
        body["fPP:j_id174:nomeAdv"] = ""
        body["fPP:j_id183:classeProcessualProcessoHidden"] = ""
        body["fPP:Decoration:j_id218"] = ""
        body["fPP:j_id224"] = "fPP:j_id224"
        return body

    def _extract_other_party(self, soup: BeautifulSoup, url: str) -> List[Party]:
        return []


class Pje1GTrf5Crawler(_PjeTrf5Crawler):
    BASE_URL = "https://pje1g.trf5.jus.br"


class Pje2GTrf5Crawler(_PjeTrf5Crawler):
    BASE_URL = "https://pje2g.trf5.jus.br"


class PjeTTTrf5Crawler(_PjeTrf5Crawler):
    BASE_URL = "https://pjett.trf5.jus.br"


if __name__ == "__main__":
    crawler_tt = PjeTTTrf5Crawler(use_proxy=True)
    crawler_1g = Pje1GTrf5Crawler(use_proxy=True)
    crawler_2g = Pje2GTrf5Crawler(use_proxy=True)

    try:
        json_dump(crawler_tt.detail_process_list('877.021.348-87'))
        json_dump(crawler_1g.detail_process_list('122.934.903-00'))
        json_dump(crawler_2g.detail_process_list('532.191.715-91'))
    finally:
        crawler_1g.close()
        crawler_2g.close()
        crawler_tt.close()
