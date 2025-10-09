import dataclasses
from typing import ClassVar

from selenium.webdriver.common.by import By

from lib.webdriver.page import Page


@dataclasses.dataclass(frozen=True)
class TRF1Page(Page):
    SPINNER: ClassVar[str] = dataclasses.field(default='_viewRoot:status.start')
    CPF_INPUT: ClassVar[str] = dataclasses.field(default='fPP:dpDec:documentoParte')
    SEARCH_BUTTON: ClassVar[str] = dataclasses.field(default='fPP:searchProcessos')
    ERROR_MESSAGE: ClassVar[str] = dataclasses.field(default='fPP:j_id224')

    PROCESS_TABLE: ClassVar[str] = dataclasses.field(default='fPP:processosTable:tb')

    def cpf_input(self):
        self.driver.wait_clickable_id(self.CPF_INPUT)
        return self.driver.find_by_id(self.CPF_INPUT)

    def search_button(self):
        self.driver.wait_clickable_id(self.SEARCH_BUTTON)
        return self.driver.find_by_id(self.SEARCH_BUTTON)

    def error_message(self):
        return self.driver.find_by_id(self.ERROR_MESSAGE)

    def process_table(self):
        return self.driver.find_by_id(self.PROCESS_TABLE)

    def get_process_row(self):
        rows = self.process_table().find_elements(By.TAG_NAME, 'tr')
        assert len(rows) == 1
        return rows[0]
