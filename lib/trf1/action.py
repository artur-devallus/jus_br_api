import dataclasses
import datetime

from selenium.webdriver.common.by import By

from lib.cpf_utils import format_cpf
from lib.exceptions import LibJusBrException
from lib.models import SimpleProcessData
from lib.trf1.page import TRF1Page
from lib.webdriver.action import Action
from lib.webdriver.driver import CustomWebDriver


@dataclasses.dataclass(frozen=True)
class TRF1Action(Action[TRF1Page]):

    def search_cpf(self, cpf: str) -> 'TRF1Action':
        self.page.cpf_input().clear()
        self.driver().wait_until_input_value_by_id(self.page.CPF_INPUT, '')
        self.page.cpf_input().send_keys(format_cpf(cpf))
        self.driver().wait_until_input_value_by_id(self.page.CPF_INPUT, format_cpf(cpf))
        self.page.search_button().click()
        return self

    def _wait_row_or_error(self):
        def _predicate(driver: CustomWebDriver) -> bool:
            has_rows = len(driver.find_element(By.ID, self.page.PROCESS_TABLE).find_elements(By.TAG_NAME, "tr")) > 0
            has_alert = driver.find_by(By.ID, self.page.ERROR_MESSAGE)
            return has_rows or (has_alert and has_alert.is_displayed())

        self.driver().wait_condition(_predicate, timeout=15)

        if self.page.error_message() and self.page.error_message().is_displayed():
            raise LibJusBrException(self.page.error_message().text)
        # return self

    def extract_simple_process_data(self):
        self._wait_row_or_error()
        row = self.page.get_process_row()
        tds = row.find_elements(By.TAG_NAME, "td")
        process_class, process_details, persons = tds[1].text.split('\n')
        status, status_at = tds[2].text.rsplit('(', maxsplit=1)
        plaintiff, defendant = persons.split(' X ')
        process_number, subject = process_details.split(' - ')
        return SimpleProcessData(
            process_class=process_class.strip(),
            process_class_abv=process_number.split(' ')[0].strip(),
            process_number=process_number.split(' ')[1].strip(),
            subject=subject.strip(),
            plaintiff=plaintiff.strip(),
            defendant=defendant.strip(),
            status=status.strip(),
            last_update=datetime.datetime.strptime(
                status_at.strip().replace('(', '').replace(')', ''),
                '%d/%m/%Y %H:%M:%S'),
        )

    def extract_detailed_process_data(self):
        def _wait_window_predicate(driver: CustomWebDriver):
            return len(driver.window_handles) > 1

        self._wait_row_or_error()
        row = self.page.get_process_row()
        tds = row.find_elements(By.TAG_NAME, "td")
        tds[0].click()
        self.page.driver.wait_condition(_wait_window_predicate)

        self.page.switch_window()
        detailed_data = None
        self.page.close_current_window()
        return detailed_data
