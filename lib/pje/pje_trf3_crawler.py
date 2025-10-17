from typing import List
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from lib.date_utils import to_date_time
from lib.exceptions import LibJusBrException
from lib.format_utils import format_process_number, format_cpf
from lib.http_client import HttpClient
from lib.models import SimpleProcessData, DetailedProcessData
from lib.string_utils import only_digits


class PjeTrf3Crawler:
    BASE_URL = "https://pje1g.trf3.jus.br"

    def __init__(self):
        self._http = HttpClient(self.BASE_URL)
        self._start()

    def _start(self):
        self._enter_site()
        self._access_login()
        self._sso_auth()
        self._enter_public_query()

    def _enter_site(self):
        r = self._http.get("/")
        return r.url

    def _access_login(self):
        r = self._http.get("/pje/login.seam")
        return r.text

    def _sso_auth(self):
        r = self._http.get("/pje/authenticateSSO.seam")
        return r.url

    def _enter_public_query(self):
        r = self._http.get("/pje/listView.seam")
        return r.url

    def _get_query_soup(self, term: str) -> BeautifulSoup:
        data = {
            "AJAXREQUEST": "_viewRoot",
            "fPP:numProcesso-inputNumeroProcessoDecoration:numProcesso-inputNumeroProcesso": "",
            "mascaraProcessoReferenciaRadio": "on",
            "fPP:j_id152:processoReferenciaInput": "",
            "fPP:dnp:nomeParte": "",
            "fPP:j_id188:nomeAdv": "",
            "fPP:j_id188:classeProcessualProcessoHidden": "",
            "tipoMascaraDocumento": "on",
            "fPP:dpDec:documentoParte": "",
            "fPP:Decoration:numeroOAB": "",
            "fPP:Decoration:j_id222": "",
            "fPP:Decoration:estadoComboOAB": "org.jboss.seam.ui.NoSelectionConverter.noSelectionValue",
            "fPP": "fPP",
            "autoScroll": "",
            "javax.faces.ViewState": "j_id1",
            "fPP:j_id243": "fPP:j_id243",
            "AJAX:EVENTS_COUNT": "1"
        }
        digs = only_digits(term)
        if len(digs) == 11:
            data['fPP:dpDec:documentoParte'] = format_cpf(term)
        elif len(digs) == 20:
            data['fPP:numProcesso-inputNumeroProcessoDecoration:numProcesso-inputNumeroProcesso'] = (
                format_process_number(term)
            )
        url = urljoin(self.BASE_URL, "/pje/ConsultaPublica/listView.seam")

        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": self.BASE_URL,
            "Referer": f"{self.BASE_URL}/pje/ConsultaPublica/listView.seam",
        }

        r = self._http.post(url, data=data, headers=headers)
        soup = BeautifulSoup(r.text, 'xml').find('div', attrs=dict(id='fPP:processosGridPanel_body'))
        self._validate_soup(soup)
        return soup

    @classmethod
    def _validate_soup(cls, soup: BeautifulSoup) -> None:
        if soup is None:
            raise LibJusBrException("soup is None")
        alert = soup.find('dt')
        if alert and alert.text:
            raise LibJusBrException(alert.text)

    def query_process_list(self, term: str) -> List[SimpleProcessData]:
        soup = self._get_query_soup(term)

        rows = soup.find('tbody', attrs=dict(id='fPP:processosTable:tb')).find_all('tr')
        process_list: List[SimpleProcessData] = []
        for row in rows:
            tds = row.find_all('td')
            term_process_number = tds[1].find('b').text
            first_part, subject = term_process_number.split(' - ')
            process_class_abv, process_number = first_part.split(' ')
            plaintiff, defendant = tds[1].contents[-1].text.split(' X ')
            status, status_at = tds[2].text.rsplit('(', maxsplit=1)

            process_list.append(SimpleProcessData(
                process_class=tds[1].contents[0].text.strip(),
                process_class_abv=process_class_abv.strip(),
                process_number=process_number.strip(),
                subject=subject.strip(),
                plaintiff=plaintiff.strip(),
                defendant=defendant.strip(),
                status=status.strip(),
                last_update=to_date_time(
                    status_at.strip().replace('(', '').replace(')', '')
                ),
            ))

        return process_list

    def _extract_detailed_from_url(self, url) -> DetailedProcessData:
        main_soup = BeautifulSoup(self._http.get(url).text, features='lxml')

        return DetailedProcessData(

        )

    def detail_process_list(self, term: str) -> List[DetailedProcessData]:
        soup = self._get_query_soup(term)
        detailed_processes = []
        rows = soup.find('tbody', attrs=dict(id='fPP:processosTable:tb')).find_all('tr')
        for row in rows:
            url = self.BASE_URL + row.find('td').find('a')['onclick'].split(',')[-1].replace("'", '').replace(')', '')
            detailed_processes.append(self._extract_detailed_from_url(url))
        return detailed_processes

    def close(self):
        self._http.close()


if __name__ == "__main__":
    crawler = PjeTrf3Crawler()

    try:
        # try:
        #     crawler.query_process_list("052.137.303-45")
        # except LibJusBrException as ex:
        #     print(ex.message)
        # print(crawler.query_process_list("10551232120214013700"))
        print(crawler.detail_process_list('090.583.703-72'))
    finally:
        crawler.close()
