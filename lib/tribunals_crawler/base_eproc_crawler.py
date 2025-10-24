import abc
from typing import List
from urllib.parse import urlencode

import bs4
from bs4 import BeautifulSoup

from lib.date_utils import to_date, to_date_time
from lib.exceptions import LibJusBrException
from lib.format_utils import format_process_number, format_cpf
from lib.models import Movement, Party, DetailedProcessData, SimpleProcessData, ProcessData, AdditionalInfo, \
    MovementAttachment
from lib.string_utils import only_digits
from lib.tribunals_crawler.abstract_crawler import AbstractCrawler


class BaseEprocCrawler(AbstractCrawler):
    QUERY_URL: str

    ID_TABLE_ROWS: str = 'divInfraAreaTabela'
    ID_PROCESS_AREA: str = 'divInfraAreaProcesso'
    TABLE_ROW_WITH_CONTENT: str = 'infraTrClara'

    PROCESS_AREA_SELECTOR: str = 'fieldset#fldAssuntos > div.col-auto'
    SUBJECT_AREA_SELECTOR: str = 'fieldset#fldAssuntos > table > tr'
    PARTY_ROWS_SELECTOR: str = 'fieldset#fldPartes > table > tr'
    ADDITIONAL_INFO_SELECTOR: str = 'fieldset#fldInformacoesAdicionais > table'
    EVENT_SELECTOR: str = 'table.infraTable'

    NO_DOCUMENTS = 'Evento não gerou documento(s)'

    PARTS_SEPARATOR: str = '\xa0' * 10
    VALUES_SEPARATOR: str = '\xa0' * 3

    def _init_session(self):
        self.http.get(self.BASE_URL)

    @abc.abstractmethod
    def _solve_captcha(self, url, body, soup):
        ...

    def _get_search_body(self, url, term, soup):
        is_cpf = len(only_digits(term)) == 11
        is_process_number = len(only_digits(term)) == 20
        form_values = [(x['name'], x['value']) for x in soup.find('form', id=True).find_all('input')]
        form_values.insert(1, ('sbmNovo', 'Consultar'))
        body = []
        is_captcha_solved = False
        for i in range(len(form_values[0:len(form_values) - 2])):
            name, value = form_values[i]
            if name.startswith('rdo'):
                form_values.append((name, 'CPF'))
            elif is_process_number and i == 2:
                form_values.append((name, format_process_number(term)))
            elif is_cpf and i == 11:
                form_values.append((name, format_cpf(term)))
            elif name == 'textInfraCaptcha':
                self._solve_captcha(url, body, soup)
                is_captcha_solved = True
            else:
                body.append((name, value))
        if not is_captcha_solved:
            self._solve_captcha(url, body, soup)

        for name, value in form_values[len(form_values) - 2:]:
            if name == 'hdnInfraCaptcha':
                body.append(('hdnInfraCaptcha', '1'))
            else:
                body.append((name, value))
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

    @classmethod
    def _parse_list_row(cls, row) -> SimpleProcessData:
        process_number, plaintiff, defendant, subject, last_event = (
            list(map(lambda x: x.text.strip(), row.find_all('td')))
        )

        return SimpleProcessData(
            process_number=process_number,
            subject=subject if subject else None,
            plaintiff=plaintiff,
            defendant=defendant,
            status=last_event if last_event else None,
            process_class=None,
            process_class_abv=None,
            last_update=None,
        )

    def find_table_rows(self, soup):
        return soup.find('div', id=self.ID_TABLE_ROWS).find_all('tr')[1:]

    def query_process_list(self, term: str) -> List[SimpleProcessData]:
        soup = self._solve_and_search(term)
        return list(map(self._parse_list_row, self.find_table_rows(soup)))

    def detail_process_list(self, term: str) -> List[DetailedProcessData]:
        soup = self._solve_and_search(term)
        rows = self.find_table_rows(soup)
        rows_count = len(rows)
        details = []
        for index in range(rows_count):
            if index != 0:
                soup = self._solve_and_search(term)
                rows = self.find_table_rows(soup)

            row = rows[index]
            details.append(self._parse_detailed_row(row))
        return details

    def _parse_detailed_row(self, row):
        res = self.http.get(
            'eproc/' + row.find('td').find('a')['href'].replace('&num_chave=&', '&eventos=true&num_chave=&')
        )
        soup = BeautifulSoup(res.content, 'lxml')
        return DetailedProcessData(
            process=self._extract_process_data(soup),
            case_parties=self._extract_case_parties(soup, res.url),
            additional_info=self._extract_additional_info(soup),
            movements=self._extract_movements(soup, res.url),
        )

    def _deep_extract(self, field, body):
        label, value, other = (
            field.select_one('label').text,
            field.select_one('span').text,
            field.select_one('div')
        )
        body[label.strip()] = value.strip()
        if not other:
            return

        self._deep_extract(other, body)

    def _extract_process_data(self, soup: BeautifulSoup) -> ProcessData:
        fields = soup.select(self.PROCESS_AREA_SELECTOR)
        subjects = '  '.join(
            list(map(lambda x: x.find_all('td')[1].text, soup.select(self.SUBJECT_AREA_SELECTOR)[1:]))
        )
        data = dict()
        for field in fields:
            self._deep_extract(field, data)

        return ProcessData(
            process_number=data['Nº do Processo:'],
            accessment_date=to_date(data.get('Data de autuação:')),
            judicial_class=data.get('Classe da ação:'),
            judge_entity=data.get('Órgão Julgador:'),
            collegiate_judge_entity=data.get('Colegiado:'),
            judge=data.get('Juiz(a):'),
            subject=subjects
        )

    def _parties_table_rows(self, soup: BeautifulSoup) -> List[bs4.Tag]:
        return soup.select(self.PARTY_ROWS_SELECTOR)

    def _transform_party(self, party_text, role):
        values = list(map(str.strip, party_text.split(self.VALUES_SEPARATOR)))
        if len(values) == 4:
            _, name, document, other = values
            return Party(
                name=name.replace('- ', '', 1),
                role=role,
                documents=[self._extract_document(document)],
                other_name=other,
            )
        elif len(values) == 3:
            _, name, document = values
            return Party(
                name=name.replace('- ', '', 1),
                role=role,
                documents=[self._extract_document(document)],
            )
        elif len(values) == 2:
            name, document = values
            return Party(
                name=name.replace('- ', '', 1),
                role=role if name.startswith('- ') else 'ADVOGADO',
                documents=[self._extract_document(document)],
            )
        else:
            raise LibJusBrException(f'cannot parse values {values}')

    def _extract_main_party(self, soup: BeautifulSoup, index) -> List[Party]:
        table_rows = self._parties_table_rows(soup)
        header = table_rows[0].find_all('th')[index].text
        parties = []
        for row in table_rows[1:]:
            if row.get('class')[0] != self.TABLE_ROW_WITH_CONTENT:
                break
            value = row.find_all('td')[index]
            all_parties_text = value.text.split(self.PARTS_SEPARATOR)
            for party_text in all_parties_text:
                if party_text.strip():
                    parties.append(self._transform_party(party_text, header))
        return parties

    def _extract_active_party(self, soup: BeautifulSoup, url: str) -> List[Party]:
        return self._extract_main_party(soup, 0)

    def _extract_passive_party(self, soup: BeautifulSoup, url: str) -> List[Party]:
        return self._extract_main_party(soup, 1)

    def _extract_other_party(self, soup: BeautifulSoup, url: str) -> List[Party]:
        table_rows = self._parties_table_rows(soup)[1:]
        start_index = -1
        for i in range(len(table_rows)):
            if table_rows[i].get('class')[0] != self.TABLE_ROW_WITH_CONTENT:
                start_index = i
                break
        if start_index == -1:
            return []
        table_rows = table_rows[start_index:]
        name_rows = [table_rows[x] for x in range(len(table_rows)) if x % 2 == 0]
        value_rows = [table_rows[x] for x in range(len(table_rows)) if x % 2 != 0]
        others = []
        for name, value in zip(name_rows, value_rows):
            name_contents = name.find_all('th')
            value_contents = value.find_all('td')

            for k, v in zip(name_contents, value_contents):
                others.append(self._transform_party(
                    v.text, k.text.strip()
                ))

        return others

    def _extract_additional_info(self, soup: BeautifulSoup) -> List[AdditionalInfo]:
        additional_info = []
        tds = soup.select_one(self.ADDITIONAL_INFO_SELECTOR).find_all('td')
        if len(tds) % 2 != 0:
            tds = tds[0:len(tds) - 1]

        names = [tds[x] for x in range(len(tds)) if x % 2 == 0]
        values = [tds[x] for x in range(len(tds)) if x % 2 != 0]

        for name, value in zip(names, values):
            additional_info.append(AdditionalInfo(
                name=name.text.strip().replace(':', ''),
                value=value.text.strip(),
            ))

        return additional_info

    def _extract_movements(self, soup: BeautifulSoup, url) -> List[Movement]:
        movements = []
        rows = soup.select(self.EVENT_SELECTOR)[-1].select('tr')[1:]
        for row in rows:
            event_id, event_ts, event_des, event_user, event_docs = row.find_all('td')
            movements.append(Movement(
                description=event_des.text.strip(),
                created_at=to_date_time(event_ts.text.strip()),
                attachments=[
                    MovementAttachment(
                        document_ref=a.text.strip(),
                        document_date=None,
                    ) for a in event_docs.find_all('a')
                ] if event_docs.text != self.NO_DOCUMENTS else []
            ))
        return movements
