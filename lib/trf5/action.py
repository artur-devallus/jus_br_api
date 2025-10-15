import base64
import dataclasses
from typing import List

from selenium.common import TimeoutException, StaleElementReferenceException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.print_page_options import PrintOptions

from lib.captcha.solver import solve_image_captcha
from lib.date_utils import to_date_time, to_date
from lib.exceptions import LibJusBrException
from lib.format_utils import format_cpf, format_process_number
from lib.log_utils import get_logger
from lib.models import SimpleProcessData, DetailedProcessData, ProcessData, CaseParty, Party, Movement, \
    MovementAttachment, Attachment
from lib.string_utils import only_digits
from lib.trf5.page import TRF5Page
from lib.webdriver.action import Action

log = get_logger(__name__)


@dataclasses.dataclass(frozen=True)
class TRF5Action(Action[TRF5Page]):

    def search_term(self, term: str) -> 'TRF5Action':
        digs = only_digits(term)
        if len(digs) == 11:
            return self.search_cpf(digs)
        elif len(digs) == 20:
            return self.search_process_number(digs)
        raise LibJusBrException(f'Cannot search term {term}')

    def _cpf_is_not_stroked(self):
        try:
            return (self
                    .page
                    .cpf_label()
                    .find_elements(By.TAG_NAME, 'label')[0]
                    .get_attribute('style') == 'text-decoration: line-through;'
                    )
        except StaleElementReferenceException:
            return False

    def search_cpf(self, cpf: str) -> 'TRF5Action':
        self.page.cpf_checkbox().click()
        self.driver().wait_condition(
            lambda x: self._cpf_is_not_stroked()
        )

        cpf_input = self.page.cpf_input()

        (ActionChains(self.page.driver)
         .move_to_element(cpf_input)
         .click()
         .key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL)
         .send_keys(str(cpf))
         .perform())

        self.driver().wait_condition(lambda x: self.page.cpf_input().get_attribute('value') == format_cpf(cpf))

        return self._do_search()

    def search_process_number(self, process_number: str) -> 'TRF5Action':
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
        captcha = self.page.captcha()
        self.driver().scroll_to(captcha)
        image = captcha.screenshot_as_base64
        code = solve_image_captcha(image)
        input_el = self.page.captcha_input()
        input_el.clear()
        input_el.send_keys(code)
        self.page.driver.wait_condition(lambda x: self.page.captcha_input().get_attribute('value') == code)

    def _check_captcha_errors(self):
        self._get_rows()

    def _do_search(self, max_retries=3):
        self._solve_image_captcha()
        self.page.search_button().click()
        try:
            self._get_rows()
        except TimeoutException:
            if max_retries == 0:
                raise
            return self._do_search(max_retries - 1)
        return self

    def _get_rows(self):
        try:
            table_area = self.page.table_panel()
        except TimeoutException:
            log.error(self.page.driver.get_screenshot_as_base64())
            raise
        span = table_area.find_elements(By.TAG_NAME, 'span')[-1]
        if span and span.text == 'Foram encontrados: 0 resultados':
            raise LibJusBrException(span.text)

        return table_area.find_element(By.ID, 'consultaPublicaList2:tb').find_elements(By.XPATH, './tr')

    def get_process_list(self) -> List[SimpleProcessData]:
        rows = self._get_rows()
        process_list = []
        for index in range(len(rows)):
            row = rows[index]
            tds = row.find_elements(By.XPATH, './td')
            plaintiff, defendant = row.find_element(
                By.ID, f'consultaPublicaList2:{index}:divPartesProcesso'
            ).find_elements(By.TAG_NAME, 'td')
            process_list.append(SimpleProcessData(
                process_number=row.find_element(By.ID, f'consultaPublicaList2:{index}:divNumeroProcesso').text,
                plaintiff=plaintiff.text.replace('APELANTE', '').strip(),
                defendant=defendant.text.replace('APELADO', '').strip(),
                subject=tds[2].text,
                process_class=row.find_element(By.ID, f'consultaPublicaList2:{index}:divClasseJudicial').text,
                process_class_abv=None,
                status=tds[3].text,
                last_update=None,
            ))
        return process_list

    def _get_process_data(self):
        return ProcessData(
            process_number=self.page.process_number(),
            distribution_date=to_date(self.page.distribution_date()),
            judicial_class=self.page.judicial_class(),
            judge_entity=self.page.judge_entity(),
            collegiate_judge_entity=self.page.collegiate_judge_entity(),
            subject=self.page.subject(),
            referenced_process_number=None,
        )

    @classmethod
    def _get_party(cls, party):
        parties = []
        rows = party.find_elements(By.XPATH, './tr')
        for row in rows:
            name, role, situation = row.find_elements(By.XPATH, './td')

            parties.append(Party(
                name=name.text.strip(),
                role=role.text.strip()
            ))
        return parties

    def _get_active_case_party(self) -> List[Party]:
        return self._get_party(self.page.active_party_tbody())

    def _get_passive_case_party(self) -> List[Party]:
        return self._get_party(self.page.passive_party_tbody())

    def _get_case_parties(self):
        return CaseParty(
            active=self._get_active_case_party(),
            passive=self._get_passive_case_party(),
        )

    @classmethod
    def _is_without_attachment(cls, el):
        return 'não gerou documento' in el.text

    def _first_row_changed(self, first_row):
        try:
            txt = self.page.event_tbody().find_elements(By.XPATH, './tr')[0].find_elements(By.XPATH, './td')[1].text
            return txt != first_row
        except StaleElementReferenceException:
            return False

    def _get_movements_and_attachments(self):
        total_events = self.page.event_count()
        movements = []
        attachments = []

        current_page = 1
        while len(movements) != total_events:
            rows = self.page.event_tbody().find_elements(By.XPATH, './tr')
            firs_rowt_text = rows[0].find_elements(By.XPATH, './td')[1].text
            for row in rows:
                _, description_time, document, _ = row.find_elements(By.XPATH, './td')
                created_at, description = list(map(str.strip, description_time.text.split(' - ', maxsplit=1)))

                movements_attachments = []
                if document.text != '':
                    document.find_element(By.TAG_NAME, 'a').click()
                    self.driver().wait_windows_greather_than(2)
                    self.page.switch_window()
                    file_b64 = self.driver().print_page(PrintOptions())
                    file_bytes = base64.b64decode(file_b64)
                    file_md5 = self.read_md5(file_bytes)
                    self.page.close_current_window()

                    mv_att_created_at, mv_att_ref = document.text.split(' - ', maxsplit=1)
                    movements_attachments.append(
                        MovementAttachment(
                            document_ref=mv_att_ref.strip(),
                            document_date=to_date_time(mv_att_created_at),
                        )
                    )
                    attachments.append(Attachment(
                        created_at=to_date_time(mv_att_created_at),
                        description=mv_att_ref.strip(),
                        file_b64=file_b64,
                        file_md5=file_md5, protocol_b64=None, protocol_md5=None
                    ))

                movements.append(Movement(
                    created_at=to_date_time(created_at.strip()),
                    description=description.strip(),
                    attachments=movements_attachments
                ))

            if len(movements) == int(total_events):
                break

            self.page.next_page().click()
            current_page += 1
            self.driver().wait_condition(lambda x: self.page.current_page_value() == str(current_page))
            self.driver().wait_condition(lambda x: self._first_row_changed(firs_rowt_text))

        return movements, attachments

    def get_detailed_process(self, process_index_or_number: str = 0) -> DetailedProcessData:
        rows = self._get_rows()
        process_list = self.get_process_list()
        row = None
        if isinstance(process_index_or_number, int):
            if process_index_or_number < len(rows):
                row = rows[process_index_or_number]
        else:
            for i in range(len(process_list)):
                process = process_list[i]
                if only_digits(process.process_number) == only_digits(process_index_or_number):
                    row = rows[i]
                    break

        if row is None:
            raise LibJusBrException(f'cannot find process {process_index_or_number}')

        tds = row.find_elements(By.XPATH, './td')
        tds[0].click()

        self.driver().wait_windows_greather_than(1)
        self.page.switch_window()

        process_data = self._get_process_data()
        case_parties = self._get_case_parties()
        movements, attachments = self._get_movements_and_attachments()

        return DetailedProcessData(
            process=process_data,
            case_parties=case_parties,
            movements=movements,
            attachments=attachments
        )
