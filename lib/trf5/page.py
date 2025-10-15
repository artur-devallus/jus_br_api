import dataclasses

from selenium.webdriver.common.by import By

from lib.string_utils import only_digits
from lib.webdriver.page import Page


@dataclasses.dataclass(frozen=True)
class TRF5Page(Page):
    PROCESS_NUMBER_INPUT: str = dataclasses.field(default='consultaPublicaForm:Processo:ProcessoDecoration:Processo')
    CPF_DIV: str = dataclasses.field(
        default='consultaPublicaForm:numeroCPFCNPJ:numeroCPFCNPJRadioCPFCNPJ'
    )
    CPF_LABEL: str = dataclasses.field(
        default='consultaPublicaForm:numeroCPFCNPJ:numeroCPFCNPJRadioCPFCNPJ:j_id229'
    )
    CPF_INPUT: str = dataclasses.field(
        default='consultaPublicaForm:numeroCPFCNPJ:numeroCPFCNPJRadioCPFCNPJ:numeroCPFCNPJCPF'
    )
    CAPTCHA_IMG: str = dataclasses.field(
        default='consultaPublicaForm:captcha:captchaImg'
    )
    CAPTCHA_INPUT: str = dataclasses.field(
        default='consultaPublicaForm:captcha:j_id268:verifyCaptcha'
    )
    CAPTCHA_ERROR: str = dataclasses.field(
        default='consultaPublicaForm:captcha:j_id268:fieldcaptchaDiv'
    )
    SEARCH_BUTTON: str = dataclasses.field(default='consultaPublicaForm:pesq')

    TABLE_PANEL: str = dataclasses.field(default='consultaPublicaList2Panel_body')

    PROCESS_NUMBER_DIV: str = dataclasses.field(default='processoTrfViewView:j_id80:j_id81')
    DISTRIBUTION_DATE_DIV: str = dataclasses.field(default='processoTrfViewView:j_id94:j_id95')
    JUDGE_ENTITY_DIV: str = dataclasses.field(default='processoTrfViewView:j_id107:j_id108')
    COLLEGIATE_JUDGE_ENTITY_DIV: str = dataclasses.field(default='processoTrfViewView:j_id120:j_id121')
    JUDICIAL_CLASS_DIV: str = dataclasses.field(default='processoTrfViewView:j_id135:j_id136')
    SUBJECT_DIV: str = dataclasses.field(default='processoTrfViewView:j_id148:j_id149')

    ACTIVE_PARTY_TBODY: str = dataclasses.field(default='namegridPartesPoloAtivoList:tb')
    PASSIVE_PARTY_TBODY: str = dataclasses.field(default='namegridPartesPoloPassivoList:tb')

    EVENT_PANEL_DIV: str = dataclasses.field(default='processoEventoPanel_body')
    EVENT_TBODY: str = dataclasses.field(default='processoEvento:tb')
    PAGINATOR: str = dataclasses.field(default='j_id423:j_id424')
    CURRENT_PAGE: str = dataclasses.field(default='j_id423:j_id424Input')

    OPEN_PDF: str = dataclasses.field(default='j_id28:btnimprimir')

    def process_number_input(self):
        self.driver.wait_clickable_id(self.PROCESS_NUMBER_INPUT)
        return self.driver.find_by_id(self.PROCESS_NUMBER_INPUT)

    def cpf_checkbox(self):
        return self.driver.find_by_id(self.CPF_DIV).find_element(By.TAG_NAME, 'input')

    def cpf_label(self):
        return self.driver.find_by_id(self.CPF_DIV).find_element(By.TAG_NAME, 'label')

    def cpf_input(self):
        self.driver.wait_clickable_id(self.CPF_INPUT)
        return self.driver.find_by_id(self.CPF_INPUT)

    def search_button(self):
        self.driver.wait_clickable_id(self.SEARCH_BUTTON)
        return self.driver.find_by_id(self.SEARCH_BUTTON)

    def captcha(self):
        return self.driver.find_by_id(self.CAPTCHA_IMG)

    def captcha_input(self):
        self.driver.wait_clickable_id(self.CAPTCHA_INPUT)
        return self.driver.find_by_id(self.CAPTCHA_INPUT)

    def captcha_error(self):
        return self.driver.find_by_id(self.CAPTCHA_ERROR)

    def table_panel(self):
        self.driver.wait_visibility_id(self.TABLE_PANEL)
        return self.driver.find_by_id(self.TABLE_PANEL)

    @classmethod
    def _find_value_from_el(cls, el):
        return el.find_element(By.CLASS_NAME, 'value').text

    def process_number(self):
        return self._find_value_from_el(self.driver.find_by_id(self.PROCESS_NUMBER_DIV))

    def distribution_date(self):
        return self._find_value_from_el(self.driver.find_by_id(self.DISTRIBUTION_DATE_DIV))

    def judge_entity(self):
        return self._find_value_from_el(self.driver.find_by_id(self.JUDGE_ENTITY_DIV))

    def collegiate_judge_entity(self):
        return self._find_value_from_el(self.driver.find_by_id(self.COLLEGIATE_JUDGE_ENTITY_DIV))

    def judicial_class(self):
        return self._find_value_from_el(self.driver.find_by_id(self.JUDICIAL_CLASS_DIV))

    def subject(self):
        return self._find_value_from_el(self.driver.find_by_id(self.SUBJECT_DIV))

    def active_party_tbody(self):
        return self.driver.find_by_id(self.ACTIVE_PARTY_TBODY)

    def passive_party_tbody(self):
        return self.driver.find_by_id(self.PASSIVE_PARTY_TBODY)

    def event_tbody(self):
        return self.driver.find_by_id(self.EVENT_TBODY)

    def event_count(self):
        return only_digits(self.driver.find_by_id(self.EVENT_PANEL_DIV).find_element(By.XPATH, './span').text)

    def paginator(self):
        return self.driver.find_by_id(self.PAGINATOR)

    def next_page(self):
        tds = self.paginator().find_element(By.TAG_NAME, 'tr').find_elements(By.XPATH, './td')
        return tds[-2].find_element(By.XPATH, './div')

    def current_page_value(self):
        return self.driver.find_by_id(self.CURRENT_PAGE).get_attribute('value')

    def open_pdf(self):
        return self.driver.find_by_id(self.OPEN_PDF)
