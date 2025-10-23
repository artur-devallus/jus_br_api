# lib/pje/base_pje_crawler.py
from __future__ import annotations

import warnings
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from urllib.parse import urljoin

import bs4
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

from lib.array_utils import array_equals, print_array
from lib.date_utils import to_date, to_date_time
from lib.exceptions import LibJusBrException
from lib.format_utils import format_cpf, format_process_number
from lib.http_client import HttpClient
from lib.models import SimpleProcessData, DetailedProcessData, ProcessData, CaseParty, Movement, Party, DocumentParty
from lib.string_utils import only_digits

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)


class BasePjeCrawler(ABC):
    BASE_URL: str
    QUERY_PATH: str
    DETAIL_PATH: str
    SELECTORS: Dict[str, str]

    QUERY_BODY_TEMPLATE: Dict[str, Any]

    ACTIVE_PARTY_BINDING: str
    PASSIVE_PARTY_BINDING: str
    OTHER_PARTY_BINDING: str

    QUERY_MOVEMENTS_TEMPLATE: Dict[str, Any]

    def __init__(self, proxy: Optional[str] = None, enable_logs: bool = False):
        self.http = HttpClient(self.BASE_URL, enable_logs=enable_logs)
        if proxy:
            self.http.session.proxies = {"https": proxy, "http": proxy}
        self._init_session()
        self._view_state = 1

    def query_process_list(self, term: str) -> List[SimpleProcessData]:
        soup = self._get_query_soup(term)
        rows = soup.select(self.SELECTORS["table_rows"])
        return [self._parse_list_row(row) for row in rows]

    def detail_process_list(self, term: str) -> List[DetailedProcessData]:
        results = []
        soup = self._get_query_soup(term)
        rows = soup.select(self.SELECTORS["table_rows"])
        for row in rows:
            results.append(self._extract_detail(self._extract_detail_url(row)))
            self._update_view_state()
        return results

    def _init_session(self):
        self.http.get('/')
        self.http.get('/pje/login.seam')
        self.http.get(self.QUERY_PATH)

    def _update_view_state(self):
        self._view_state += 1

    def _get_query_soup(self, term: str) -> BeautifulSoup:
        url = urljoin(self.BASE_URL, self.QUERY_PATH)
        data = self._build_query_body(term)
        headers = self._build_headers(url)
        response = self.http.post(url, data=data, headers=headers)

        soup = BeautifulSoup(response.text, 'lxml')
        container = soup.select_one(self.SELECTORS["table_container"])
        if not container:
            raise LibJusBrException("Não foi possível encontrar a tabela de resultados.")
        self._update_view_state()
        return container

    def _post_query_detail(self, referer, data) -> BeautifulSoup:
        url = urljoin(self.BASE_URL, self.DETAIL_PATH)
        headers = self._build_headers(referer)
        response = self.http.post(url, data=data, headers=headers)

        return BeautifulSoup(response.text, 'lxml')

    def _build_headers(self, referer: str) -> Dict[str, str]:
        return {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": self.BASE_URL,
            "Referer": referer,
        }

    def _build_query_body(self, term: str) -> Dict[str, Any]:
        body = dict(self.QUERY_BODY_TEMPLATE)
        digs = only_digits(term)
        if len(digs) == 11:
            body['fPP:dpDec:documentoParte'] = format_cpf(term)
        elif len(digs) == 20:
            body['fPP:numProcesso-inputNumeroProcessoDecoration:numProcesso-inputNumeroProcesso'] = (
                format_process_number(term)
            )
        return body

    def _parse_list_row(self, row) -> SimpleProcessData:
        tds = row.find_all('td')
        term_process_number = tds[1].find('b').text
        first_part, subject = term_process_number.split(' - ')
        process_class_abv, process_number = first_part.split(' ')
        plaintiff, defendant = tds[1].contents[-1].text.split(' X ')
        status, status_at = tds[2].text.rsplit('(', maxsplit=1)

        return SimpleProcessData(
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
        )

    def _extract_detail_url(self, row: bs4.Tag) -> str:
        return self.BASE_URL + row.find('td').find('a')['onclick'].split(',')[-1].replace("'", '').replace(')', '')

    def _extract_detail(self, url: str) -> DetailedProcessData:
        html = self.http.get(url).text
        soup = BeautifulSoup(html, 'lxml')
        return DetailedProcessData(
            process=self._extract_process_data(soup),
            case_parties=self._extract_case_parties(soup, url),
            movements=self._extract_movements(soup),
        )

    @classmethod
    def _parse_property(cls, tag):
        text = tag.text.strip().split('\n')[-1].strip()
        if not text:
            return None
        return text

    def _extract_process_data(self, soup: BeautifulSoup) -> ProcessData:
        span_tags = soup.select(self.SELECTORS["process_data"])
        span_dict = {
            tg.select_one('div > div.name').text.strip(): tg.select_one('div > div.value').text.strip()
            for tg in span_tags
        }
        if span_dict.get(''):
            del span_dict['']
            empties = [
                tg.select_one('div > div.value > div') for tg in span_tags if
                tg.select_one('div > div.name').text.strip() == ''
            ]
            for empty in empties:
                key, val = empty.text.strip().split('\n', maxsplit=1)
                span_dict[key] = val.strip().replace('\t', '').replace('\n\n', ' - ')

        return ProcessData(
            process_number=span_dict['Número Processo'],
            distribution_date=to_date(span_dict['Data da Distribuição']),
            judicial_class=span_dict['Classe Judicial'],
            subject=span_dict['Assunto'],
            jurisdiction=span_dict['Jurisdição'],
            collegiate_judge_entity=span_dict.get('Órgão Julgador Colegiado'),
            judge_entity=span_dict.get('Órgão Julgador'),
            referenced_process_number=span_dict.get('Processo referência'),
        )

    def _build_party_body(self, page: int, binding: str) -> Dict[str, Any]:
        next_binding = int(only_digits(binding.split(':')[-1])) + 1
        page_binding = binding + ':' + f'j_id{next_binding}'
        return {
            "AJAXREQUEST": "_viewRoot",
            binding: binding,
            'javax.faces.ViewState': f'j_id{self._view_state}',
            'ajaxSingle': page_binding,
            page_binding: str(page),
            "AJAX:EVENTS_COUNT": "1"
        }

    def _build_active_party_body(self, page: int) -> Dict[str, Any]:
        return self._build_party_body(page, self.ACTIVE_PARTY_BINDING)

    def _build_passive_party_body(self, page: int) -> Dict[str, Any]:
        return self._build_party_body(page, self.PASSIVE_PARTY_BINDING)

    def _build_other_party_body(self, page: int) -> Dict[str, Any]:
        return self._build_party_body(page, self.OTHER_PARTY_BINDING)

    @classmethod
    def _get_table_binding_for(cls, binding):
        parts = binding.split(':')
        return ':'.join(parts[0:len(parts) - 1]) + ':tb'

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
    def _map_tag_to_party(cls, tag) -> Party:
        party_txt = tag.find('td').text
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

    def _map_soup_to_parties(self, soup, binding) -> List[Party]:
        return [self._map_tag_to_party(x) for x in soup.select(
            'tbody#' + self._get_table_binding_for(binding).replace(':', '\\:') + ' > tr'
        )]

    def _extract_paginated_parties(self, referer, binding, body_fn) -> List[Party]:
        page = 2
        all_parties = []
        last_rows = []
        while True:
            tmp_soup = self._post_query_detail(referer, body_fn(page))
            tmp_rows = self._map_soup_to_parties(tmp_soup, binding)
            if len(tmp_rows) < 10 or array_equals(last_rows, tmp_rows):
                break

            last_rows = tmp_rows
            print_array(tmp_rows)
            all_parties.extend(tmp_rows)
            print(f'finished active party page {page}')
            page += 1
        return all_parties

    def _extract_party(self, soup: BeautifulSoup, url, binding, body_fn) -> List[Party]:
        parties = self._map_soup_to_parties(soup, binding)
        if len(parties) == 10:
            parties.extend(
                self._extract_paginated_parties(url, binding, body_fn)
            )
        return parties

    def _extract_active_party(self, soup: BeautifulSoup, url: str) -> List[Party]:
        return self._extract_party(
            soup, url, self.ACTIVE_PARTY_BINDING, self._build_active_party_body
        )

    def _extract_passive_party(self, soup: BeautifulSoup, url: str) -> List[Party]:
        return self._extract_party(
            soup, url, self.PASSIVE_PARTY_BINDING, self._build_passive_party_body
        )

    def _extract_other_party(self, soup: BeautifulSoup, url: str) -> List[Party]:
        return self._extract_party(
            soup, url, self.OTHER_PARTY_BINDING, self._build_other_party_body
        )

    def _extract_case_parties(self, soup: BeautifulSoup, url) -> CaseParty:
        return CaseParty(
            active=self._extract_active_party(soup, url),
            passive=self._extract_passive_party(soup, url),
            others=self._extract_other_party(soup, url),
        )

    @abstractmethod
    def _extract_movements(self, soup: BeautifulSoup) -> List[Movement]:
        ...

    def close(self):
        self.http.close()
