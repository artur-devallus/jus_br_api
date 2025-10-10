import dataclasses

from selenium.webdriver.common.by import By

from lib.string_utils import only_digits
from lib.webdriver.page import Page


@dataclasses.dataclass(frozen=True)
class PJePage(Page):
    CPF_INPUT: str = dataclasses.field()

    PROCESS_NUMBER_INPUT: str = dataclasses.field()
    SEARCH_BUTTON: str = dataclasses.field()
    ERROR_MESSAGE: str = dataclasses.field()

    PROCESS_TABLE: str = dataclasses.field()

    PROCESS_NUMBER: str = dataclasses.field()
    DISTRIBUTION_DATE: str = dataclasses.field()
    JUDICIAL_CLASS: str = dataclasses.field()
    SUBJECT: str = dataclasses.field()
    JURISDICTION: str = dataclasses.field()
    COLLEGIATE_JUDGE_ENTITY: str = dataclasses.field()
    JUDGE_ENTITY: str = dataclasses.field()
    REFERENCED_PROCESS_NUMBER: str = dataclasses.field()
    ACTIVE_PARTY_TABLE_BODY: str = dataclasses.field()
    PASSIVE_PARTY_TABLE_BODY: str = dataclasses.field()

    MOVEMENTS_PANEL_BODY: str = dataclasses.field()
    MOVEMENTS_TABLE_BODY: str = dataclasses.field()
    MOVEMENT_PAGE_INPUT: str = dataclasses.field()

    ATTACHMENTS_PANEL_BODY: str = dataclasses.field()
    ATTACHMENTS_TABLE_BODY: str = dataclasses.field()
    ATTACHMENT_PAGE_INPUT: str = dataclasses.field()
    DOWNLOAD_PDF_FILE: str = dataclasses.field()

    QUERY_PROCESS: str = dataclasses.field(
        default="//a[text()[contains(.,'Consulta')]]"
    )

    def query_process(self):
        self.driver.wait_presence(By.XPATH, self.QUERY_PROCESS)
        return self.driver.find_by_xpath(self.QUERY_PROCESS)

    def cpf_input(self):
        self.driver.wait_clickable_id(self.CPF_INPUT)
        return self.driver.find_by_id(self.CPF_INPUT)

    def process_number_input(self):
        self.driver.wait_clickable_id(self.PROCESS_NUMBER_INPUT)
        return self.driver.find_by_id(self.PROCESS_NUMBER_INPUT)

    def search_button(self):
        self.driver.wait_clickable_id(self.SEARCH_BUTTON)
        return self.driver.find_by_id(self.SEARCH_BUTTON)

    def error_message_text(self):
        els = self.driver.find_elements(By.CLASS_NAME, self.ERROR_MESSAGE)
        return els[0].text if len(els) else None

    def process_table(self):
        return self.driver.find_by_id(self.PROCESS_TABLE)

    def get_process_rows(self):
        return self.process_table().find_elements(By.TAG_NAME, 'tr')

    @classmethod
    def _last_div_text(cls, el):
        if not el:
            return None
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

    def collegiate_judge_entity(self):
        els = self.driver.find_elements(By.ID, self.COLLEGIATE_JUDGE_ENTITY)
        return self._last_div_text(els[0] if len(els) else None)

    def referenced_process_number(self):
        els = self.driver.find_elements(By.ID, self.REFERENCED_PROCESS_NUMBER)
        return self._last_div_text(els[0] if len(els) else None)

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

    def attachments_quantity(self):
        return int(only_digits(self.driver.find_by_id(self.ATTACHMENTS_PANEL_BODY).find_element(
            By.CLASS_NAME, 'pull-right'
        ).get_attribute('textContent')))

    def attachments_table_body(self):
        return self.driver.find_by_id(self.ATTACHMENTS_TABLE_BODY)

    def attachments_page_input(self):
        return self.driver.find_by_id(self.ATTACHMENT_PAGE_INPUT)

    def download_pdf_file(self):
        return self.driver.find_by_id(self.DOWNLOAD_PDF_FILE, timeout=2)


@dataclasses.dataclass(frozen=True)
class TRF1PJePage(PJePage):
    CPF_INPUT: str = dataclasses.field(default='fPP:dpDec:documentoParte')
    PROCESS_NUMBER_INPUT: str = dataclasses.field(
        default='fPP:numProcesso-inputNumeroProcessoDecoration:numProcesso-inputNumeroProcesso'
    )
    SEARCH_BUTTON: str = dataclasses.field(default='fPP:searchProcessos')
    ERROR_MESSAGE: str = dataclasses.field(default='alert-danger')

    PROCESS_TABLE: str = dataclasses.field(default='fPP:processosTable:tb')

    PROCESS_NUMBER: str = dataclasses.field(default='j_id136:processoTrfViewView:j_id144')
    DISTRIBUTION_DATE: str = dataclasses.field(default='j_id136:processoTrfViewView:j_id156')
    JUDICIAL_CLASS: str = dataclasses.field(default='j_id136:processoTrfViewView:j_id167')
    SUBJECT: str = dataclasses.field(default='j_id136:processoTrfViewView:j_id178')
    JURISDICTION: str = dataclasses.field(default='j_id136:processoTrfViewView:j_id191')
    COLLEGIATE_JUDGE_ENTITY: str = dataclasses.field(default='j_id136:processoTrfViewView:j_id202')
    JUDGE_ENTITY: str = dataclasses.field(default='j_id136:processoTrfViewView:j_id215')
    REFERENCED_PROCESS_NUMBER: str = dataclasses.field(default='j_id136:processoTrfViewView:j_id226')
    ACTIVE_PARTY_TABLE_BODY: str = dataclasses.field(
        default='j_id136:processoPartesPoloAtivoResumidoTableBinding:tb'
    )
    PASSIVE_PARTY_TABLE_BODY: str = dataclasses.field(
        default='j_id136:processoPartesPoloPassivoResumidoTableBinding:tb'
    )

    MOVEMENTS_PANEL_BODY: str = dataclasses.field(
        default='j_id136:processoEventoPanel_body'
    )
    MOVEMENTS_TABLE_BODY: str = dataclasses.field(
        default='j_id136:processoEvento:tb'
    )
    MOVEMENT_PAGE_INPUT: str = dataclasses.field(default='j_id136:j_id546:j_id547Input')

    ATTACHMENTS_PANEL_BODY: str = dataclasses.field(default='j_id136:processoDocumentoGridTabPanel_body')
    ATTACHMENTS_TABLE_BODY: str = dataclasses.field(default='j_id136:processoDocumentoGridTab:tb')
    ATTACHMENT_PAGE_INPUT: str = dataclasses.field(default='j_id136:j_id648:j_id649Input')

    DOWNLOAD_PDF_FILE: str = dataclasses.field(
        default='j_id42:downloadPDF'
    )


@dataclasses.dataclass(frozen=True)
class TRF3PJePage(PJePage):
    CPF_INPUT: str = dataclasses.field(default='fPP:dpDec:documentoParte')
    PROCESS_NUMBER_INPUT: str = dataclasses.field(
        default='fPP:numProcesso-inputNumeroProcessoDecoration:numProcesso-inputNumeroProcesso'
    )
    SEARCH_BUTTON: str = dataclasses.field(default='fPP:searchProcessos')
    ERROR_MESSAGE: str = dataclasses.field(default='alert-danger')

    PROCESS_TABLE: str = dataclasses.field(default='fPP:processosTable:tb')

    PROCESS_NUMBER: str = dataclasses.field(default='j_id145:processoTrfViewView:j_id153')
    DISTRIBUTION_DATE: str = dataclasses.field(default='j_id145:processoTrfViewView:j_id165')
    JUDICIAL_CLASS: str = dataclasses.field(default='j_id145:processoTrfViewView:j_id176')
    SUBJECT: str = dataclasses.field(default='j_id145:processoTrfViewView:j_id187')
    JURISDICTION: str = dataclasses.field(default='j_id145:processoTrfViewView:j_id200')
    COLLEGIATE_JUDGE_ENTITY: str = dataclasses.field(default='j_id145:processoTrfViewView:j_id211')
    JUDGE_ENTITY: str = dataclasses.field(default='j_id145:processoTrfViewView:j_id224')
    REFERENCED_PROCESS_NUMBER: str = dataclasses.field(default='j_id145:processoTrfViewView:j_id237')

    ACTIVE_PARTY_TABLE_BODY: str = dataclasses.field(
        default='j_id145:processoPartesPoloAtivoResumidoList:tb'
    )
    PASSIVE_PARTY_TABLE_BODY: str = dataclasses.field(
        default='j_id145:processoPartesPoloPassivoResumidoList:tb'
    )

    MOVEMENTS_PANEL_BODY: str = dataclasses.field(default='j_id145:processoEventoPanel_body')
    MOVEMENTS_TABLE_BODY: str = dataclasses.field(default='j_id145:processoEvento:tb')
    MOVEMENT_PAGE_INPUT: str = dataclasses.field(default='j_id145:j_id556:j_id557Input')

    ATTACHMENTS_PANEL_BODY: str = dataclasses.field(default='j_id145:processoDocumentoGridTabPanel_body')
    ATTACHMENTS_TABLE_BODY: str = dataclasses.field(default='j_id145:processoDocumentoGridTab:tb')
    ATTACHMENT_PAGE_INPUT: str = dataclasses.field(default='j_id145:j_id648:j_id649Input')
    DOWNLOAD_PDF_FILE: str = dataclasses.field(default='j_id39:downloadPDF')


@dataclasses.dataclass(frozen=True)
class TRF5PJePage(PJePage):
    CPF_INPUT: str = dataclasses.field(default='fPP:dpDec:documentoParte')
    PROCESS_NUMBER_INPUT: str = dataclasses.field(
        default='fPP:numProcesso-inputNumeroProcessoDecoration:numProcesso-inputNumeroProcesso'
    )
    SEARCH_BUTTON: str = dataclasses.field(default='fPP:searchProcessos')
    ERROR_MESSAGE: str = dataclasses.field(default='alert-danger')

    PROCESS_TABLE: str = dataclasses.field(default='fPP:processosTable:tb')

    PROCESS_NUMBER: str = dataclasses.field(default='j_id140:processoTrfViewView:j_id146')
    DISTRIBUTION_DATE: str = dataclasses.field(default='j_id140:processoTrfViewView:j_id158')
    JUDICIAL_CLASS: str = dataclasses.field(default='j_id140:processoTrfViewView:j_id169')
    SUBJECT: str = dataclasses.field(default='j_id140:processoTrfViewView:j_id180')
    JURISDICTION: str = dataclasses.field(default='j_id140:processoTrfViewView:j_id193')
    COLLEGIATE_JUDGE_ENTITY: str = dataclasses.field(default='j_id140:processoTrfViewView:j_id204')
    JUDGE_ENTITY: str = dataclasses.field(default='j_id140:processoTrfViewView:j_id217')
    REFERENCED_PROCESS_NUMBER: str = dataclasses.field(default='j_id140:processoTrfViewView:j_id230')

    ACTIVE_PARTY_TABLE_BODY: str = dataclasses.field(
        default='j_id140:processoPartesPoloAtivoResumidoList:tb'
    )
    PASSIVE_PARTY_TABLE_BODY: str = dataclasses.field(
        default='j_id140:processoPartesPoloPassivoResumidoList:tb'
    )

    MOVEMENTS_PANEL_BODY: str = dataclasses.field(default='j_id140:processoEventoPanel_body')
    MOVEMENTS_TABLE_BODY: str = dataclasses.field(default='j_id140:processoEvento:tb')
    MOVEMENT_PAGE_INPUT: str = dataclasses.field(default='j_id140:j_id545:j_id546Input')

    ATTACHMENTS_PANEL_BODY: str = dataclasses.field(default='j_id140:processoDocumentoGridTabPanel_body')
    ATTACHMENTS_TABLE_BODY: str = dataclasses.field(default='j_id140:processoDocumentoGridTab:tb')
    ATTACHMENT_PAGE_INPUT: str = dataclasses.field(default='j_id140:j_id648:j_id649Input')
    DOWNLOAD_PDF_FILE: str = dataclasses.field(default='j_id39:downloadPDF')
