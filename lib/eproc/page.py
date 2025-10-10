import dataclasses

from selenium.webdriver.common.by import By

from lib.webdriver.page import Page


@dataclasses.dataclass(frozen=True)
class EprocPage(Page):
    DATA_AREA: str = dataclasses.field(default='divInfraAreaDados')
    SEARCH_BUTTON: str = dataclasses.field(default='sbmNovo')
    CAPTCHA_DIV: str = dataclasses.field(default='divInfraCaptcha')
    TABLE_AREA: str = dataclasses.field(default='divInfraAreaTabela')

    def _inputs(self):
        return self.driver.find_by_id(self.DATA_AREA).find_elements(By.TAG_NAME, 'input')

    def process_number_input(self):
        el_id = self._inputs()[0].get_attribute('id')
        self.driver.wait_clickable_id(el_id)
        return self.driver.find_by_id(el_id)

    def cpf_input(self):
        el_id = self._inputs()[9].get_attribute('id')
        self.driver.wait_clickable_id(el_id)
        return self.driver.find_by_id(el_id)

    def search_button(self):
        self.driver.wait_clickable_id(self.SEARCH_BUTTON)
        return self.driver.find_by_id(self.SEARCH_BUTTON)

    def captcha(self):
        return self.driver.find_by_id(self.CAPTCHA_DIV)

    def table_area(self):
        self.driver.wait_visibility_id(self.TABLE_AREA)
        return self.driver.find_by_id(self.TABLE_AREA)