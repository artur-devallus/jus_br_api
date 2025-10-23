from lib.json_utils import json_dump
from lib.pje.base_pje_crawler import BasePjeCrawler


class _PjeTrf1Crawler(BasePjeCrawler):
    QUERY_PATH = "/consultapublica/ConsultaPublica/listView.seam"
    DETAIL_PATH = "/consultapublica/ConsultaPublica/DetalheProcessoConsultaPublica/listView.seam"

    ACTIVE_PARTY_BINDING = 'j_id136:processoPartesPoloAtivoResumidoTableBinding:j_id325'
    PASSIVE_PARTY_BINDING = 'j_id136:processoPartesPoloPassivoResumidoTableBinding:j_id390'
    OTHER_PARTY_BINDING = 'j_id136:processoParteOutrosInteressadosResumidoTableBinding:j_id455'

    MOVEMENT_AJAX_REQUEST = 'j_id136:j_id465'
    MOVEMENT_AJAX_BINDING = 'j_id136:j_id546'

    def _build_query_body(self, term):
        body = super()._build_query_body(term)
        body["fPP:j_id170:nomeAdv"] = ""
        body["fPP:j_id179:classeProcessualProcessoHidden"] = ""
        body["fPP:Decoration:j_id214"] = ""
        body["fPP:j_id220"] = "fPP:j_id220"
        return body


class Pje1GTrf1Crawler(_PjeTrf1Crawler):
    BASE_URL = "https://pje1g.trf1.jus.br"


class Pje2GTrf1Crawler(_PjeTrf1Crawler):
    BASE_URL = "https://pje2g.trf1.jus.br"


if __name__ == "__main__":
    crawler_1g = Pje1GTrf1Crawler(use_proxy=True)
    crawler_2g = Pje2GTrf1Crawler(use_proxy=True)

    try:
        json_dump(crawler_1g.detail_process_list('13132434850'))
        json_dump(crawler_2g.detail_process_list('13132434850'))
    finally:
        crawler_1g.close()
        crawler_2g.close()
