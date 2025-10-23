import dataclasses
import json
from typing import List

from bs4 import BeautifulSoup

from lib.json_utils import default_json_encoder, json_dump
from lib.models import Party
from lib.pje.base_pje_crawler import BasePjeCrawler


class _PjeTrf3Crawler(BasePjeCrawler):
    QUERY_PATH = "/pje/ConsultaPublica/listView.seam"
    DETAIL_PATH = "/pje/ConsultaPublica/DetalheProcessoConsultaPublica/listView.seam"


    ACTIVE_PARTY_BINDING = 'j_id145:processoPartesPoloAtivoResumidoList:j_id336'
    PASSIVE_PARTY_BINDING = 'j_id145:processoPartesPoloPassivoResumidoList:j_id400'

    MOVEMENT_AJAX_REQUEST = 'j_id145:j_id473'
    MOVEMENT_AJAX_BINDING = 'j_id145:j_id556'

    def _build_query_body(self, term):
        body = super()._build_query_body(term)
        body["fPP:j_id188:nomeAdv"] = ""
        body["fPP:j_id188:classeProcessualProcessoHidden"] = ""
        body["fPP:Decoration:j_id222"] = ""
        body["fPP:j_id243"] = "fPP:j_id243"
        return body

    def _extract_other_party(self, soup: BeautifulSoup, url: str) -> List[Party]:
        return []


class Pje1GTrf3Crawler(_PjeTrf3Crawler):
    BASE_URL = "https://pje1g.trf3.jus.br"


class Pje2GTrf3Crawler(_PjeTrf3Crawler):
    BASE_URL = "https://pje2g.trf3.jus.br"


if __name__ == "__main__":
    crawler_1g = Pje1GTrf3Crawler(use_proxy=True)
    crawler_2g = Pje2GTrf3Crawler(use_proxy=True)

    try:
        json_dump(crawler_1g.detail_process_list('535.920.778-72'))
        json_dump(crawler_2g.detail_process_list('535.920.778-72'))
    finally:
        crawler_1g.close()
        crawler_2g.close()
