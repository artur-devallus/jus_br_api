import dataclasses

from selenium.webdriver.common.by import By

from lib.webdriver.page import Page


@dataclasses.dataclass(frozen=True)
class EprocPage(Page):
    DATA_AREA: str = dataclasses.field(default='divInfraAreaDados')
    SEARCH_BUTTON: str = dataclasses.field(default='sbmNovo')
    CAPTCHA_DIV: str = dataclasses.field(default='divInfraCaptcha')
    TURNSTILE_RESPONSE: str = dataclasses.field(default='cf-turnstile-response')
    TABLE_AREA: str = dataclasses.field(default='divInfraAreaTabela')

    PROCESS_NUMBER: str = dataclasses.field(default='txtNumProcesso')
    ASSESSMENT_DATE: str = dataclasses.field(default='txtAutuacao')
    STATUS: str = dataclasses.field(default='txtSituacao')
    JUDGE_ENTITY: str = dataclasses.field(default='txtOrgaoJulgador')
    JUDGE: str = dataclasses.field(default='txtMagistrado')
    JUDICIAL_CLASS: str = dataclasses.field(default='txtClasse')
    RELATED_PROCESS_TABLE: str = dataclasses.field(default='tableRelacionado')
    SUBJECT_FIELDSET: str = dataclasses.field(default='fldAssuntos')

    PARTY_FIELDSET: str = dataclasses.field(default='fldPartes')

    PROCESS_AREA: str = dataclasses.field(default='divInfraAreaProcesso')
    SHOW_ALL_EVENTS: str = dataclasses.field(default="//a[text()[contains(.,'listar todos os eventos')]]")

    CONTENT_IFRAME: str = dataclasses.field(default='conteudoIframe')
    OPEN_PDF: str = dataclasses.field(default='open-button')

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

    def process_number(self):
        return self.driver.find_by_id(self.PROCESS_NUMBER).text

    def accessment_date(self):
        return self.driver.find_by_id(self.ASSESSMENT_DATE).text

    def status(self):
        return self.driver.find_by_id(self.STATUS).text

    def judge(self):
        return self.driver.find_by_id(self.JUDGE).text

    def judge_entity(self):
        return self.driver.find_by_id(self.JUDGE_ENTITY).text

    def judicial_class(self):
        return self.driver.find_by_id(self.JUDICIAL_CLASS).text

    def referenced_process_number(self):
        tables = self.driver.find_elements(
            By.ID, self.RELATED_PROCESS_TABLE
        )
        if not tables:
            return None
        tb = tables[0].find_element(
            By.TAG_NAME, 'tbody'
        )
        if not tb:
            return None
        rows = tb.find_elements(By.TAG_NAME, 'tr')[-1]
        return rows.find_elements(By.TAG_NAME, 'td')[0].text

    def subject(self):
        return ' '.join([' - '.join([y.text for y in
                                     x.find_elements(By.TAG_NAME, 'td')[:2]]) for x in
                         self.driver.find_by_id(self.SUBJECT_FIELDSET).find_element(
                             By.TAG_NAME, 'table'
                         ).find_elements(By.TAG_NAME, 'tr')[1:]])

    def _get_parties(self, index_td):
        rows = self.driver.find_by_id(self.PARTY_FIELDSET).find_element(
            By.TAG_NAME, 'table'
        ).find_elements(By.TAG_NAME, 'tr')[1:]

        els = []
        for row in rows:
            els.append(row.find_elements(By.TAG_NAME, 'td')[index_td].text)

        return els

    def active_parties(self):
        return self._get_parties(0)

    def passive_parties(self):
        return self._get_parties(1)

    def show_all_events(self):
        return self.driver.find_by_xpath(self.SHOW_ALL_EVENTS)

    def event_rows(self):
        return self.driver.find_by_id(self.PROCESS_AREA).find_elements(
            By.TAG_NAME, 'table'
        )[-1].find_elements(By.TAG_NAME, 'tr')[1:]

    def turnstile_response(self):
        return self.driver.find_by_name(self.TURNSTILE_RESPONSE)

    def content_iframe(self):
        return self.driver.find_by_id(self.CONTENT_IFRAME)

    def open_pdf(self):
        return self.driver.find_by_id(self.OPEN_PDF)
