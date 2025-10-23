from typing import Dict, Any, List

from bs4 import BeautifulSoup

from lib.date_utils import to_date_time
from lib.format_utils import format_cpf, format_process_number
from lib.models import Movement
from lib.pje.base_pje_crawler import BasePjeCrawler
from lib.string_utils import only_digits


class PjeTrf1Crawler(BasePjeCrawler):
    BASE_URL = "https://pje1g.trf1.jus.br"
    QUERY_PATH = "/consultapublica/ConsultaPublica/listView.seam"
    DETAIL_PATH = "/consultapublica/ConsultaPublica/DetalheProcessoConsultaPublica/listView.seam"

    SELECTORS = {
        'table_container': "div#fPP\\:processosGridPanel_body",
        'table_rows': "tbody#fPP\\:processosTable\\:tb > tr",
        'viewstate': "input[name='javax.faces.ViewState']",
        'process_data': 'div#j_id136\\:processoTrfViewView\\:j_id139_body > table > tbody > tr > td > span'
    }

    QUERY_BODY_TEMPLATE = {
        "AJAXREQUEST": "_viewRoot",
        "fPP:numProcesso-inputNumeroProcessoDecoration:numProcesso-inputNumeroProcesso": "",
        "mascaraProcessoReferenciaRadio": "on",
        "fPP:j_id152:processoReferenciaInput": "",
        "fPP:dnp:nomeParte": "",
        "fPP:j_id170:nomeAdv": "",
        "fPP:j_id179:classeProcessualProcessoHidden": "",
        "tipoMascaraDocumento": "on",
        "fPP:dpDec:documentoParte": "",
        "fPP:Decoration:numeroOAB": "",
        "fPP:Decoration:j_id214": "",
        "fPP:Decoration:estadoComboOAB": "org.jboss.seam.ui.NoSelectionConverter.noSelectionValue",
        "fPP": "fPP",
        "autoScroll": "",
        "javax.faces.ViewState": "j_id1",
        "fPP:j_id220": "fPP:j_id220",
        "AJAX:EVENTS_COUNT": "1"
    }

    ACTIVE_PARTY_BINDING = 'j_id136:processoPartesPoloAtivoResumidoTableBinding:j_id325'
    PASSIVE_PARTY_BINDING = 'j_id136:processoPartesPoloPassivoResumidoTableBinding:j_id390'
    OTHER_PARTY_BINDING = 'j_id136:processoParteOutrosInteressadosResumidoTableBinding:j_id455'

    QUERY_MOVEMENTS_TEMPLATE = {

    }

    def _extract_movements(self, soup: BeautifulSoup) -> List[Movement]:
        movements = []
        for row in soup.select("table tr"):
            cols = [td.text.strip() for td in row.find_all("td")]
            if len(cols) >= 2:
                movements.append(Movement(date=to_date_time(cols[0]), description=cols[1]))
        return movements


if __name__ == "__main__":
    crawler = PjeTrf1Crawler()

    try:
        # try:
        #     crawler.query_process_list("052.137.303-45")
        # except LibJusBrException as ex:
        #     print(ex.message)
        # print(crawler.query_process_list("10551232120214013700"))
        print(crawler.detail_process_list('090.583.703-72'))
    finally:
        crawler.close()
