from lib.json_utils import json_dump
from lib.tribunals_crawler.base_pje_crawler import BasePjeCrawler


class _PjeTrf5Crawler(BasePjeCrawler):
    QUERY_PATH = "/pjeconsulta/ConsultaPublica/listView.seam"
    DETAIL_PATH = "/pjeconsulta/ConsultaPublica/DetalheProcessoConsultaPublica/listView.seam"

    def _build_query_body(self, term):
        body = super()._build_query_body(term)
        body["fPP:j_id174:nomeAdv"] = ""
        body["fPP:j_id183:classeProcessualProcessoHidden"] = ""
        body["fPP:Decoration:j_id218"] = ""
        body["fPP:j_id224"] = "fPP:j_id224"
        return body


class Pje1GTrf5Crawler(_PjeTrf5Crawler):
    BASE_URL = "https://pje1g.trf5.jus.br"


class Pje2GTrf5Crawler(_PjeTrf5Crawler):
    BASE_URL = "https://pje2g.trf5.jus.br"


class PjeTTTrf5Crawler(_PjeTrf5Crawler):
    BASE_URL = "https://pjett.trf5.jus.br"


if __name__ == "__main__":
    # crawler_tt = PjeTTTrf5Crawler(use_proxy=True)
    crawler_1g = Pje1GTrf5Crawler(use_proxy=True)
    # crawler_2g = Pje2GTrf5Crawler(use_proxy=True)

    try:
        json_dump(crawler_1g.detail_process_list('374.424.064-91'))
        # json_dump(crawler_tt.detail_process_list('877.021.348-87'))
        # json_dump(crawler_2g.detail_process_list('532.191.715-91'))
    finally:
        crawler_1g.close()
        # crawler_2g.close()
        # crawler_tt.close()
