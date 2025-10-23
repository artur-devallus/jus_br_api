import warnings
from typing import List
from urllib.parse import urljoin

import bs4
from bs4 import BeautifulSoup
from bs4 import XMLParsedAsHTMLWarning

from lib.array_utils import print_array, array_equals
from lib.date_utils import to_date_time, to_date
from lib.exceptions import LibJusBrException
from lib.format_utils import format_process_number, format_cpf
from lib.http_client import HttpClient
from lib.models import SimpleProcessData, DetailedProcessData, Party, DocumentParty, Movement, MovementAttachment, \
    CaseParty, ProcessData
from lib.string_utils import only_digits

warnings.filterwarnings('ignore', category=XMLParsedAsHTMLWarning)


class PjeTrf1Crawler:
    BASE_URL = "https://pje1g.trf1.jus.br"

    def __init__(self):
        self._http = HttpClient(self.BASE_URL)
        self._start()
        self._current_id = 1

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
        r = self._http.get("/pje/ConsultaPublica/listView.seam")
        return r.url

    def _get_query_soup(self, term: str) -> BeautifulSoup:
        data = {
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
        digs = only_digits(term)
        if len(digs) == 11:
            data['fPP:dpDec:documentoParte'] = format_cpf(term)
        elif len(digs) == 20:
            data['fPP:numProcesso-inputNumeroProcessoDecoration:numProcesso-inputNumeroProcesso'] = (
                format_process_number(term)
            )
        url = urljoin(self.BASE_URL, "/consultapublica/ConsultaPublica/listView.seam")

        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": self.BASE_URL,
            "Referer": f"{self.BASE_URL}/consultapublica/ConsultaPublica/listView.seam",
        }

        r = self._http.post(url, data=data, headers=headers)
        soup = BeautifulSoup(r.text, 'xml').find('div', attrs=dict(id='fPP:processosGridPanel_body'))
        self._validate_soup(soup)
        self._current_id += 1
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
            process=self.process(main_soup),
            case_parties=self.case_parties(main_soup, url),
            movements=self.movements(main_soup, url),
        )

    @classmethod
    def property_value(cls, tag) -> str | None:
        return tag.find_all('div')[-1].text.strip() if tag and len(tag.find_all('div')) else None

    def process(self, main_soup) -> ProcessData:
        return ProcessData(
            process_number=self.property_value(
                main_soup.find('span', attrs=dict(id='j_id136:processoTrfViewView:j_id144'))
            ),
            distribution_date=to_date(self.property_value(
                main_soup.find('span', attrs=dict(id='j_id136:processoTrfViewView:j_id156'))
            )),
            jurisdiction=self.property_value(
                main_soup.find('span', attrs=dict(id='j_id136:processoTrfViewView:j_id191'))
            ),
            judicial_class=self.property_value(
                main_soup.find('span', attrs=dict(id='j_id136:processoTrfViewView:j_id167'))
            ),
            judge_entity=self.property_value(
                main_soup.find('span', attrs=dict(id='j_id136:processoTrfViewView:j_id215'))
            ),
            collegiate_judge_entity=self.property_value(
                main_soup.find('span', attrs=dict(id='j_id136:processoTrfViewView:j_id202'))
            ),
            referenced_process_number=self.property_value(
                main_soup.find('span', attrs=dict(id='j_id136:processoTrfViewView:j_id226'))
            ),
            subject=self.property_value(
                main_soup.find('span', attrs=dict(id='j_id136:processoTrfViewView:j_id178'))
            ),
        )

    def case_parties(self, main_soup, url):
        return CaseParty(
            active=self.polo_ativo(main_soup, url),
            passive=self.polo_passivo(main_soup, url),
            others=self.outros(main_soup, url)
        )

    @classmethod
    def _extract_document(cls, doc) -> DocumentParty | None:
        doc = str(doc).upper()
        only_digits_doc = only_digits(doc)
        if 'CPF' in str(doc):
            return DocumentParty.of_cpf(
                doc
                .replace('CPF', '')
                .replace('.', '')
                .replace('-', '')
                .replace(':', '')
                .strip()
            )
        elif 'CNPJ' in str(doc):
            return DocumentParty.of_cnpj(
                doc
                .replace('CNPJ', '')
                .replace('.', '')
                .replace('-', '')
                .replace(':', '')
                .replace('/', '')
                .strip()
            )
        elif 'OAB' in str(doc):
            return DocumentParty.of_oab(doc.replace('OAB', '').strip())
        if only_digits_doc:
            raise LibJusBrException(f'cannot get document for {doc}')
        return DocumentParty.of_unknown(doc)

    @classmethod
    def _party_from_text(cls, party_txt) -> Party:
        parts = party_txt.split(' - ')
        documents = parts[1:len(parts) - 1]
        last_document, role = parts[len(parts) - 1].split(' (')
        documents.append(last_document.strip())
        role_and_other = str(role.replace(')', '').strip()).rsplit('\n', 1)

        role = role_and_other[0].strip()
        other = role_and_other[1].strip() if len(role_and_other) > 1 else None
        name = parts[0].strip()
        if ' registrado(a) civilmente como ' in name:
            other, name = name.split(' registrado(a) civilmente como ')

        return Party(
            name=name,
            documents=list(filter(lambda x: x is not None, [cls._extract_document(doc) for doc in documents])),
            role=role,
            other_name=other,
        )

    def _polo_ativo_soup(self, page, referer: str) -> BeautifulSoup:
        data = {
            "AJAXREQUEST": "_viewRoot",
            'j_id136:processoPartesPoloAtivoResumidoTableBinding:j_id325': 'j_id136:processoPartesPoloAtivoResumidoTableBinding:j_id325',
            'javax.faces.ViewState': f'j_id{self._current_id}',
            'ajaxSingle': 'j_id136:processoPartesPoloAtivoResumidoTableBinding:j_id325:j_id326',
            'j_id136:processoPartesPoloAtivoResumidoTableBinding:j_id325:j_id326': str(page),
            "AJAX:EVENTS_COUNT": "1"
        }
        url = f'{self.BASE_URL}/consultapublica/ConsultaPublica/DetalheProcessoConsultaPublica/listView.seam'

        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": self.BASE_URL,
            "Referer": referer,
        }

        r = self._http.post(url, data=data, headers=headers)
        return BeautifulSoup(r.text, 'lxml')

    def _other_interesteds_soup(self, page, referer: str) -> BeautifulSoup:
        data = {
            "AJAXREQUEST": "_viewRoot",
            'j_id136:processoParteOutrosInteressadosResumidoTableBinding:j_id455': 'j_id136:processoParteOutrosInteressadosResumidoTableBinding:j_id455',
            'javax.faces.ViewState': f'j_id{self._current_id}',
            'ajaxSingle': 'j_id136:processoParteOutrosInteressadosResumidoTableBinding:j_id455:j_id456',
            'j_id136:processoParteOutrosInteressadosResumidoTableBinding:j_id455:j_id456': str(page),
            "AJAX:EVENTS_COUNT": "1"
        }
        url = f'{self.BASE_URL}/consultapublica/ConsultaPublica/DetalheProcessoConsultaPublica/listView.seam'

        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": self.BASE_URL,
            "Referer": referer,
        }

        r = self._http.post(url, data=data, headers=headers)
        return BeautifulSoup(r.text, 'lxml')

    def _passive_parties_soup(self, page, referer: str) -> BeautifulSoup:
        data = {
            "AJAXREQUEST": "_viewRoot",
            'j_id136:processoPartesPoloPassivoResumidoTableBinding:j_id390': 'j_id136:processoPartesPoloPassivoResumidoTableBinding:j_id390',
            'javax.faces.ViewState': f'j_id{self._current_id}',
            'ajaxSingle': 'j_id136:processoPartesPoloPassivoResumidoTableBinding:j_id390:j_id391',
            'j_id136:processoPartesPoloPassivoResumidoTableBinding:j_id390:j_id391': str(page),
            "AJAX:EVENTS_COUNT": "1"
        }
        url = f'{self.BASE_URL}/consultapublica/ConsultaPublica/DetalheProcessoConsultaPublica/listView.seam'

        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": self.BASE_URL,
            "Referer": referer,
        }

        r = self._http.post(url, data=data, headers=headers)
        return BeautifulSoup(r.text, 'lxml')

    def _movements_soup(self, page, referer: str) -> BeautifulSoup:
        data = {
            "AJAXREQUEST": "j_id136:j_id465",
            "j_id136:j_id546:j_id547": str(page),
            'j_id136:j_id546': 'j_id136:j_id546',
            'autoScroll': '',
            'javax.faces.ViewState': f'j_id{self._current_id}',
            'j_id136:j_id546:j_id548': 'j_id136:j_id546:j_id548',
            "AJAX:EVENTS_COUNT": "1"
        }

        url = f'{self.BASE_URL}/consultapublica/ConsultaPublica/DetalheProcessoConsultaPublica/listView.seam'

        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": self.BASE_URL,
            "Referer": referer,
        }

        r = self._http.post(url, data=data, headers=headers)
        return BeautifulSoup(r.text, 'lxml')

    def polo_ativo(self, main_soup: BeautifulSoup, referer: str) -> List[Party]:
        extract_rows_fn = lambda soup: [
            self._party_from_text(x.find('td').text)
            for x in soup.find(
                'tbody', attrs=dict(id='j_id136:processoPartesPoloAtivoResumidoTableBinding:tb')
            ).find_all('tr')
        ]
        parties: List[Party] = extract_rows_fn(main_soup)
        if len(parties) < 10:
            return parties
        page = 2
        last_rows = []
        while True:
            tmp_soup = self._polo_ativo_soup(page, referer)
            tmp_rows = extract_rows_fn(tmp_soup)
            if len(tmp_rows) < 10 or array_equals(last_rows, tmp_rows):
                break

            last_rows = tmp_rows
            print_array(tmp_rows)
            parties.extend(tmp_rows)
            print(f'finished active party page {page}')
            page += 1

        return parties

    def outros(self, main_soup: BeautifulSoup, referer: str) -> List[Party]:
        extract_rows_fn = lambda soup: [
            self._party_from_text(x.find('td').text)
            for x in soup.find(
                'tbody', attrs=dict(id='j_id136:processoParteOutrosInteressadosResumidoTableBinding:tb')
            ).find_all('tr')
        ]
        others: List[Party] = extract_rows_fn(main_soup)
        if len(others) < 10:
            return others
        page = 2
        last_rows = []
        while True:
            tmp_soup = self._other_interesteds_soup(page, referer)
            tmp_rows = extract_rows_fn(tmp_soup)
            if len(tmp_rows) < 10 or array_equals(last_rows, tmp_rows):
                break

            last_rows = tmp_rows
            print_array(tmp_rows)
            others.extend(tmp_rows)
            print(f'finished others page {page}')
            page += 1

        return others

    def polo_passivo(self, main_soup: BeautifulSoup, referer: str) -> List[Party]:
        extract_rows_fn = lambda soup: [
            self._party_from_text(x.find('td').text)
            for x in soup.find(
                'tbody', attrs=dict(id='j_id136:processoPartesPoloPassivoResumidoTableBinding:tb')
            ).find_all('tr')
        ]
        passive: List[Party] = extract_rows_fn(main_soup)
        if len(passive) < 10:
            return passive
        page = 2
        last_rows = []
        while True:
            tmp_soup = self._passive_parties_soup(page, referer)
            tmp_rows = extract_rows_fn(tmp_soup)
            if len(tmp_rows) < 10 or array_equals(last_rows, tmp_rows):
                break

            last_rows = tmp_rows
            print_array(tmp_rows)
            passive.extend(tmp_rows)
            print(f'finished passive page {page}')
            page += 1

        return passive

    @classmethod
    def _movement_from_tr(cls, tr: bs4.Tag) -> Movement:
        td1, td2 = [x.text for x in tr.find_all('td')]
        created_at, description = td1.split(' - ', maxsplit=1)
        if td2:
            document_date, document_ref = td2.split(' - ', maxsplit=1)
        else:
            document_ref = None
            document_date = None
        return Movement(
            created_at=to_date_time(created_at),
            description=description,
            attachments=[MovementAttachment(
                document_date=to_date_time(
                    document_date
                ) if document_date else None,
                document_ref=document_ref,
            )] if document_ref else []
        )

    def movements(self, main_soup: BeautifulSoup, referer: str) -> List[Movement]:
        extract_movements_fn = lambda soup: [
            self._movement_from_tr(x)
            for x in soup.find(
                'tbody', attrs=dict(id='j_id136:processoEvento:tb')
            ).find_all('tr')
        ]
        movements: List[Movement] = extract_movements_fn(main_soup)
        if len(movements) < 15:
            return movements
        page = 2
        last_rows = []
        while True:
            tmp_soup = self._movements_soup(page, referer)
            tmp_rows = extract_movements_fn(tmp_soup)
            if len(tmp_rows) < 15 or array_equals(last_rows, tmp_rows):
                break

            last_rows = tmp_rows
            print_array(tmp_rows)
            movements.extend(tmp_rows)
            print(f'finished movements page {page}')
            page += 1

        return movements

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
