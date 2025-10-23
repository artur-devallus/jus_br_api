from lib.pje.base_pje_crawler import BasePjeCrawler


class PjeTrf1Crawler(BasePjeCrawler):
    BASE_URL = "https://pje1g.trf1.jus.br"

    QUERY_PATH = "/consultapublica/ConsultaPublica/listView.seam"
    DETAIL_PATH = "/consultapublica/ConsultaPublica/DetalheProcessoConsultaPublica/listView.seam"

    SELECTOR_PROCESS_DATA = 'div#j_id136\\:processoTrfViewView\\:j_id139_body > table > tbody > tr > td > span'

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


if __name__ == "__main__":
    crawler = PjeTrf1Crawler()

    try:
        # try:
        #     crawler.query_process_list("052.137.303-45")
        # except LibJusBrException as ex:
        #     print(ex.message)
        # print(crawler.query_process_list("10551232120214013700"))
        print(crawler.detail_process_list('13132434850'))
    finally:
        crawler.close()
