from lib.json_utils import json_dump
from lib.tribunals_crawler.base_pje_crawler import BasePjeCrawler


class _PjeTrf3Crawler(BasePjeCrawler):
    QUERY_PATH = "/pje/ConsultaPublica/listView.seam"
    DETAIL_PATH = "/pje/ConsultaPublica/DetalheProcessoConsultaPublica/listView.seam"

    def _build_query_body(self, term):
        body = super()._build_query_body(term)
        body["fPP:j_id188:nomeAdv"] = ""
        body["fPP:j_id188:classeProcessualProcessoHidden"] = ""
        body["fPP:Decoration:j_id222"] = ""
        body["fPP:j_id243"] = "fPP:j_id243"
        return body


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
