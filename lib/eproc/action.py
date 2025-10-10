import dataclasses
from typing import List

from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By

from lib.captcha.solver import solve_image_captcha
from lib.date_utils import to_date_time
from lib.eproc.page import EprocPage
from lib.exceptions import LibJusBrException
from lib.format_utils import format_cpf, format_process_number
from lib.models import SimpleProcessData, DetailedProcessData
from lib.string_utils import only_digits
from lib.webdriver.action import Action


@dataclasses.dataclass(frozen=True)
class EprocAction(Action[EprocPage]):

    def search_term(self, term: str) -> 'EprocAction':
        digs = only_digits(term)
        if len(digs) == 11:
            return self.search_cpf(digs)
        elif len(digs) == 20:
            return self.search_process_number(digs)
        raise LibJusBrException(f'Cannot search term {term}')

    def search_cpf(self, cpf: str) -> 'EprocAction':
        cpf_input = self.page.cpf_input()

        (ActionChains(self.page.driver)
         .move_to_element(cpf_input)
         .click()
         .key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL)
         .send_keys(str(cpf))
         .perform())

        self.driver().wait_condition(lambda x: self.page.cpf_input().get_attribute('value') == format_cpf(cpf))

        return self._do_search()

    def search_process_number(self, process_number: str) -> 'EprocAction':
        process_number_input = self.page.process_number_input()

        (ActionChains(self.page.driver)
         .move_to_element(process_number_input)
         .click()
         .key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL)
         .send_keys(str(format_process_number(process_number)))
         .perform())

        return self._do_search()

    @classmethod
    def _solve_manual(cls):
        return input('Solve captcha!')

    def _solve_image_captcha(self):
        image = self.page.captcha().find_element(By.TAG_NAME, 'img').get_attribute('src')
        code = solve_image_captcha(image)
        input_el = self.page.captcha().find_element(By.TAG_NAME, 'input')
        input_id = input_el.get_attribute('id')
        input_el.send_keys(code)
        self.page.driver.wait_condition(lambda x: x.find_by_id(input_id).get_attribute('value') == code)

    def _solve_cloudflare(self):
        ...

    @classmethod
    def _is_image_captcha(cls, el):
        return len(el.find_elements(By.TAG_NAME, 'img'))

    @classmethod
    def _is_cloudflare_captcha(cls, el):
        if not len(el.find_elements(By.TAG_NAME, 'div')):
            return False
        return 'cf-turnstile' in el.find_element(By.TAG_NAME, 'div').get_attribute('class')

    def solve_captcha(self):
        captcha = self.page.captcha()
        # if not self.page.driver.is_headless():
        #     return self._solve_manual()
        if self._is_image_captcha(captcha):
            return self._solve_image_captcha()
        elif self._is_cloudflare_captcha(captcha):
            return self._solve_cloudflare()
        raise LibJusBrException('Unsolvable captcha')

    def _do_search(self):
        self.solve_captcha()
        self.page.search_button().click()
        return self

    def _get_rows(self):
        table_area = self.page.table_area()
        if not table_area.find_elements(By.TAG_NAME, 'table'):
            raise LibJusBrException(table_area.text.strip())

        return table_area.find_element(By.TAG_NAME, 'table').find_element(By.TAG_NAME, 'tbody').find_elements(
            By.TAG_NAME, 'tr'
        )[1:]

    def get_process_list(self) -> List[SimpleProcessData]:
        rows = self._get_rows()
        process_list = []
        for row in rows:
            ths = row.find_elements(By.TAG_NAME, 'td')
            process_list.append(SimpleProcessData(
                process_number=ths[0].text,
                plaintiff=ths[1].text,
                defendant=ths[2].text,
                subject=ths[3].text or 'Assunto não disponível',
                process_class=None,
                process_class_abv=None,
                status=None,
                last_update=to_date_time(ths[4].text) if ths[4].text else None,
            ))
        return process_list

    def get_detailed_process(self, process_index_or_number: str = 0) -> DetailedProcessData:
        rows = self._get_rows()
        row = None
        if isinstance(process_index_or_number, int):
            if process_index_or_number < len(rows):
                row = rows[process_index_or_number]
        else:
            process_list = self.get_process_list()
            for i in range(len(process_list)):
                process = process_list[i]
                if only_digits(process.process_number) == only_digits(process_index_or_number):
                    row = rows[process_index_or_number]
                    break

        if row is None:
            raise LibJusBrException(f'cannot find process {process_index_or_number}')

        tds = row.find_elements(By.TAG_NAME, "td")
        tds[0].click()

        return None
