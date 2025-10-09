import dataclasses
import datetime

from selenium.webdriver.common.by import By

from lib.cpf_utils import format_cpf
from lib.models import SimpleProcessData
from lib.trf1.page import TRF1Page
from lib.webdriver.action import Action
from lib.webdriver.driver import CustomWebDriver


@dataclasses.dataclass(frozen=True)
class TRF1Action(Action[TRF1Page]):

    def search_cpf(self, cpf: str) -> 'TRF1Action':
        self.page.cpf_input().clear()
        self.page.cpf_input().send_keys(format_cpf(cpf))
        self.driver().wait_until_input_value_by_id(self.page.CPF_INPUT, format_cpf(cpf))
        self.page.search_button().click()
        return self

    def extract_simple_process_data(self):
        def _predicate(driver: CustomWebDriver) -> bool:
            return len(driver.find_element(By.ID, self.page.PROCESS_TABLE).find_elements(By.TAG_NAME, "tr")) > 0

        self.driver().wait_condition(_predicate, timeout=15)
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
