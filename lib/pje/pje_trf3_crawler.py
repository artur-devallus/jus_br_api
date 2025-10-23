import dataclasses
import json
from typing import List

from bs4 import BeautifulSoup

from lib.json_utils import default_json_encoder
from lib.models import Party
from lib.pje.base_pje_crawler import BasePjeCrawler
from lib.proxy.proxies import fastest_proxy


class PjeTrf3Crawler(BasePjeCrawler):
    BASE_URL = "https://pje1g.trf3.jus.br"
    QUERY_PATH = "/pje/ConsultaPublica/listView.seam"
    DETAIL_PATH = "/pje/ConsultaPublica/DetalheProcessoConsultaPublica/listView.seam"

    SELECTOR_PROCESS_DATA = 'div#j_id145\\:processoTrfViewView\\:j_id148_body > table > tbody > tr > td > span'

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


if __name__ == "__main__":
    crawler = PjeTrf3Crawler(
        proxy=fastest_proxy("https://pje1g.trf3.jus.br")
    )

    try:
        # try:
        #     crawler.query_process_list("052.137.303-45")
        # except LibJusBrException as ex:
        #     print(ex.message)
        data = crawler.detail_process_list("0009022-07.2002.4.03.6301")
        for o in data:
            print(json.dumps(
                dataclasses.asdict(o),
                default=default_json_encoder,
                indent=2
            ))
        data = crawler.detail_process_list('535.920.778-72')
        for o in data:
            print(json.dumps(
                dataclasses.asdict(o),
                default=default_json_encoder,
                indent=2
            ))
    finally:
        crawler.close()
