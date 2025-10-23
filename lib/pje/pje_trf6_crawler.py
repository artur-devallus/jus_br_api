from typing import List

from bs4 import BeautifulSoup

from lib.json_utils import json_dump
from lib.models import Party
from lib.pje.base_pje_crawler import BasePjeCrawler


class _PjeTrf6Crawler(BasePjeCrawler):
    QUERY_PATH = "/consultapublica/ConsultaPublica/listView.seam"
    DETAIL_PATH = "/consultapublica/ConsultaPublica/DetalheProcessoConsultaPublica/listView.seam"

    def _build_query_body(self, term):
        body = super()._build_query_body(term)
        body["fPP:j_id176:nomeAdv"] = ""
        body["fPP:j_id185:classeProcessualProcessoHidden"] = ""
        body["fPP:Decoration:j_id220"] = ""
        body["fPP:j_id226"] = "fPP:j_id226"
        return body

class Pje1GTrf6Crawler(_PjeTrf6Crawler):
    BASE_URL = "https://pje1g.trf6.jus.br"


class Pje2GTrf6Crawler(_PjeTrf6Crawler):
    BASE_URL = "https://pje2g.trf6.jus.br"



if __name__ == "__main__":
    crawler_1g = Pje1GTrf6Crawler(use_proxy=True)
    crawler_2g = Pje2GTrf6Crawler(use_proxy=True)

    try:
        json_dump(crawler_1g.detail_process_list('227.026.956-04'))
        json_dump(crawler_2g.detail_process_list('315.622.216-04'))
    finally:
        crawler_1g.close()
        crawler_2g.close()
