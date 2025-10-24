import abc
from collections import OrderedDict
from typing import List
from urllib.parse import urlencode

from bs4 import BeautifulSoup

from lib.array_utils import last_index_of
from lib.format_utils import format_process_number, format_cpf
from lib.models import Movement, Party, DetailedProcessData, SimpleProcessData
from lib.string_utils import only_digits
from lib.tribunals_crawler.abstract_crawler import AbstractCrawler


class BaseEprocCrawler(AbstractCrawler):
    QUERY_URL: str

    def _init_session(self):
        self.http.get(self.BASE_URL)

    @abc.abstractmethod
    def _solve_captcha(self, url, body, soup):
        ...

    def _get_search_body(self, url, term, soup):
        body = [
            ('hdnInfraTipoPagina', '1'),
            ('sbmNovo', 'Consultar'),
        ]
        first_parts = [1, 2, 3, 4]
        second_parts = [7, 8, 10, 11]
        all_inputs_ids = [(x['id'], x['value']) for x in soup.find('form', id=True).find_all('input')]
        for index in first_parts:
            body.append(all_inputs_ids[index])
        body.append((all_inputs_ids[6][0], 'N'))
        body.append((all_inputs_ids[6][0], 'S'))
        for index in second_parts:
            body.append(all_inputs_ids[index])

        is_cpf = len(only_digits(term)) == 11
        if not is_cpf:
            input_id, _ = all_inputs_ids[1]
            body.append((input_id, format_process_number(term)))
        else:
            only_ids = [x[0] for x in all_inputs_ids]
            input_id, _ = all_inputs_ids[last_index_of(only_ids, lambda el: str(el).startswith('rdo')) + 1]
            body.append((input_id, format_cpf(term)))

        body = self._solve_captcha(url, body, soup)

        body.append(('hdnInfraCaptcha', '1'))
        body.append(('hdnInfraSelecoes', 'Infra'))
        return body

    def _solve_and_search(self, term):
        response = self.http.get(self.QUERY_URL)
        soup = BeautifulSoup(response.content, 'lxml')
        body = self._get_search_body(response.url, term, soup)
        form = soup.find('form', id=True)
        path_split = response.url.path.split('/')
        full_url = '/'.join(path_split[0:len(path_split) - 1] + [form['action']])
        response = self.http.post(full_url, urlencode(body), headers={
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': self.BASE_URL,
            'Referer': str(self.BASE_URL + self.QUERY_URL),
        })
        return BeautifulSoup(response.content, 'lxml')

    def query_process_list(self, term: str) -> List[SimpleProcessData]:
        soup = self._solve_and_search(term)
        return []

    def detail_process_list(self, term: str) -> List[DetailedProcessData]:
        soup = self._solve_and_search(term)
        return []

    def _extract_active_party(self, soup: BeautifulSoup, url: str) -> List[Party]:
        pass

    def _extract_passive_party(self, soup: BeautifulSoup, url: str) -> List[Party]:
        pass

    def _extract_other_party(self, soup: BeautifulSoup, url: str) -> List[Party]:
        pass

    def _extract_movements(self, soup: BeautifulSoup, url) -> List[Movement]:
        pass
