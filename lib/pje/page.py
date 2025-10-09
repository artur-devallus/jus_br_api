import dataclasses
from typing import ClassVar

from selenium.webdriver.common.by import By

from lib.string_utils import only_digits
from lib.webdriver.page import Page


@dataclasses.dataclass(frozen=True)
class PJePage(Page):
    SPINNER: ClassVar[str] = dataclasses.field(default='_viewRoot:status.start')
    CPF_INPUT: ClassVar[str] = dataclasses.field(default='fPP:dpDec:documentoParte')
    SEARCH_BUTTON: ClassVar[str] = dataclasses.field(default='fPP:searchProcessos')
    ERROR_MESSAGE: ClassVar[str] = dataclasses.field(default='fPP:j_id224')

    PROCESS_TABLE: ClassVar[str] = dataclasses.field(default='fPP:processosTable:tb')

    PROCESS_NUMBER: ClassVar[str] = dataclasses.field(default='j_id136:processoTrfViewView:j_id144')
    DISTRIBUTION_DATE: ClassVar[str] = dataclasses.field(default='j_id136:processoTrfViewView:j_id156')
    JURISDICTION: ClassVar[str] = dataclasses.field(default='j_id136:processoTrfViewView:j_id191')
    JUDICIAL_CLASS: ClassVar[str] = dataclasses.field(default='j_id136:processoTrfViewView:j_id167')
    JUDGE_ENTITY: ClassVar[str] = dataclasses.field(default='j_id136:processoTrfViewView:j_id215')
    SUBJECT: ClassVar[str] = dataclasses.field(default='j_id136:processoTrfViewView:j_id178')
    ACTIVE_PARTY_TABLE_BODY: ClassVar[str] = dataclasses.field(
        default='j_id136:processoPartesPoloAtivoResumidoTableBinding:tb'
    )
    PASSIVE_PARTY_TABLE_BODY: ClassVar[str] = dataclasses.field(
        default='j_id136:processoPartesPoloPassivoResumidoTableBinding:tb'
    )

    MOVEMENTS_PANEL_BODY: ClassVar[str] = dataclasses.field(
        default='j_id136:processoEventoPanel_body'
    )
    MOVEMENTS_TABLE_BODY: ClassVar[str] = dataclasses.field(
        default='j_id136:processoEvento:tb'
    )
    MOVEMENT_PAGE_INPUT: ClassVar[str] = dataclasses.field(default='j_id136:j_id546:j_id547Input')

    ATTACHMENTS_TABLE_BODY: ClassVar[str] = dataclasses.field(
        default='j_id136:processoDocumentoGridTab:tb'
    )
    DOWNLOAD_PDF_FILE: ClassVar[str] = dataclasses.field(
        default='j_id42:downloadPDF'
    )

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

    @classmethod
    def _last_div_text(cls, el):
        return el.find_elements(By.TAG_NAME, 'div')[-1].text

    def process_number(self):
        return self._last_div_text(self.driver.find_by_id(self.PROCESS_NUMBER))

    def distribution_date(self):
        return self._last_div_text(self.driver.find_by_id(self.DISTRIBUTION_DATE))

    def jurisdiction(self):
        return self._last_div_text(self.driver.find_by_id(self.JURISDICTION))

    def judicial_class(self):
        return self._last_div_text(self.driver.find_by_id(self.JUDICIAL_CLASS))

    def judge_entity(self):
        return self._last_div_text(self.driver.find_by_id(self.JUDGE_ENTITY))

    def subject(self):
        return self._last_div_text(self.driver.find_by_id(self.SUBJECT))

    def get_active_party_table_body(self):
        return self.driver.find_by_id(self.ACTIVE_PARTY_TABLE_BODY)

    def get_passive_party_table_body(self):
        return self.driver.find_by_id(self.PASSIVE_PARTY_TABLE_BODY)

    def movements_quantity(self):
        return int(only_digits(self.driver.find_by_id(self.MOVEMENTS_PANEL_BODY).find_element(
            By.CLASS_NAME, 'pull-right'
        ).get_attribute('textContent')))

    def movements_table(self):
        return self.driver.find_by_id(self.MOVEMENTS_TABLE_BODY)

    def movements_page_input(self):
        return self.driver.find_by_id(self.MOVEMENT_PAGE_INPUT)

    def attachments_table_body(self):
        return self.driver.find_by_id(self.ATTACHMENTS_TABLE_BODY)

    def download_pdf_file(self):
        return self.driver.find_by_id(self.DOWNLOAD_PDF_FILE)