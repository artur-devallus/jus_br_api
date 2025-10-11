import dataclasses
from typing import List

from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By

from lib.captcha.solver import solve_image_captcha, solve_cloudflare_captcha
from lib.date_utils import to_date_time, to_date
from lib.eproc.page import EprocPage
from lib.exceptions import LibJusBrException
from lib.format_utils import format_cpf, format_process_number
from lib.log_utils import get_logger
from lib.models import SimpleProcessData, DetailedProcessData, ProcessData, CaseParty, Party, Movement, DocumentParty, \
    MovementAttachment, Attachment
from lib.string_utils import only_digits
from lib.webdriver.action import Action

log = get_logger(__name__)


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
        cf_div = self.page.captcha().find_element(By.TAG_NAME, 'div')
        site_key = cf_div.get_attribute('data-sitekey')
        token = solve_cloudflare_captcha(site_key, self.driver().current_url)
        input_turnstile = self.page.turnstile_response()
        self.driver().execute_script("arguments[0].value = arguments[1];", input_turnstile, token)

        self.driver().wait_condition(
            lambda x: x.find_by_name(self.page.TURNSTILE_RESPONSE).get_attribute('value') == token
        )

        self.driver().execute_script("""
            let event = new Event('change', { bubbles: true });
            arguments[0].dispatchEvent(event);
        """, input_turnstile)
        self.driver().execute_script("""
            if (window.callbackCloudflare) {
                window.callbackCloudflare(arguments[0]);
            }
        """, token)

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

    def _get_process_data(self):
        return ProcessData(
            process_number=self.page.process_number(),
            distribution_date=None,
            accessment_date=to_date(self.page.accessment_date()),
            jurisdiction=None,
            judicial_class=self.page.judicial_class(),
            judge_entity=self.page.judge_entity(),
            collegiate_judge_entity=None,
            referenced_process_number=self.page.referenced_process_number(),
            subject=self.page.subject(),
        )

    @classmethod
    def _extract_document(cls, doc):
        doc = doc.replace('(', '').replace(')', '').strip()
        if '**************' in str(doc):
            return DocumentParty.of_cnpj(
                doc.strip()
            )
        elif '**********' in str(doc):
            return DocumentParty.of_cpf(
                doc.strip()
            )
        elif len(only_digits(doc)) > 3:
            return DocumentParty.of_oab(doc)
        log.warning(f'cannot determine document {doc}')
        return DocumentParty.of_unknown(doc)

    def _extract_party(self, txt):
        person, doc = txt.split('   ')
        doc = self._extract_document(doc)
        return Party(
            name=str(person).strip().replace('- ', '', 1),
            documents=[doc] if doc else [],
            role=None,
        )

    def _get_party(self, party_list):
        parties = []
        for party in party_list:
            splited = list(map(str.strip, party.split('\n')))
            for part_split in splited:
                if not part_split:
                    continue
                parties.append(self._extract_party(part_split))
        return parties

    def _get_active_case_party(self) -> List[Party]:
        return self._get_party(self.page.active_parties())

    def _get_passive_case_party(self) -> List[Party]:
        return self._get_party(self.page.passive_parties())

    def _get_case_parties(self):
        return CaseParty(
            active=self._get_active_case_party(),
            passive=self._get_passive_case_party(),
        )

    @classmethod
    def _is_without_attachment(cls, el):
        return 'não gerou documento' in el.text

    def _get_movements(self):
        events = self.page.event_rows()
        movements = []
        for event in events:
            event_id, date_hour, description, _, docs = event.find_elements(By.TAG_NAME, 'td')
            movements.append(Movement(
                created_at=to_date_time(date_hour.text),
                description=description.text,
                attachments=[] if self._is_without_attachment(docs) else [
                    MovementAttachment(
                        document_ref=x.text
                    ) for x in docs.find_elements(By.TAG_NAME, 'a')
                ]
            ))
        return movements

    def _get_attachments(self):
        events = self.page.event_rows()
        attachments = []
        for event in events:
            _, _, _, _, docs = event.find_elements(By.TAG_NAME, 'td')
            if self._is_without_attachment(docs):
                continue
            anchors = event.find_elements(By.TAG_NAME, 'a')
            for anchor in anchors:
                anchor.click()
                self.page.switch_window()
                self.driver().switch_to.frame(self.page.content_iframe())
                self.page.open_pdf().click()
                file_b64, file_md5 = self.read_file_remove_and_close()

                attachments.append(Attachment(
                    created_at=None,
                    description=anchor.text,
                    file_md5=file_md5,
                    file_b64=file_b64,
                    protocol_b64=None,
                    protocol_md5=None,
                ))
        return attachments

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

        self.page.show_all_events().click()

        return DetailedProcessData(
            process=self._get_process_data(),
            case_parties=self._get_case_parties(),
            movements=self._get_movements(),
            attachments=self._get_attachments()
        )
