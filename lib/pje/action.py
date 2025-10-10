import base64
import dataclasses
import os
from typing import List

from selenium.common import StaleElementReferenceException, TimeoutException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By

from lib.date_utils import to_date_time, to_date, is_date_time
from lib.exceptions import LibJusBrException
from lib.format_utils import format_cpf, format_process_number
from lib.log_utils import get_logger
from lib.models import (
    SimpleProcessData,
    DetailedProcessData,
    ProcessData,
    CaseParty,
    Party,
    DocumentParty,
    Movement,
    Attachment
)
from lib.pje.constants import QUERY_TIMEOUT
from lib.pje.page import PJePage
from lib.string_utils import only_digits
from lib.webdriver.action import Action
from lib.webdriver.driver import CustomWebDriver

log = get_logger(__name__)


def _first_row_changed_predicate(driver, id_table, first_row_text):
    try:
        current_text = driver.find_element(
            By.ID, id_table
        ).find_elements(By.TAG_NAME, 'tr')[0].find_element(
            By.TAG_NAME, 'td'
        ).text
        return first_row_text != current_text
    except StaleElementReferenceException:
        return False


def _window_handles_gt_predicate(driver, expected_len):
    return len(driver.window_handles) > expected_len


@dataclasses.dataclass(frozen=True)
class PJeAction(Action[PJePage]):

    def enter_site(self) -> 'PJeAction':
        if 'Denied' in self.page.driver.title:
            raise LibJusBrException(f'Access denied for {self.page.driver.current_url}')
        self.page.query_process().click()
        self.page.driver.wait_condition(lambda x: _window_handles_gt_predicate(x, 1))
        self.page.close_current_window()
        return self

    def search_term(self, term: str) -> 'PJeAction':
        digs = only_digits(term)
        if len(digs) == 11:
            return self.search_cpf(digs)
        elif len(digs) == 20:
            return self.search_process_number(digs)
        raise LibJusBrException(f'Cannot search term {term}')

    def search_cpf(self, cpf: str) -> 'PJeAction':
        cpf_input = self.page.cpf_input()

        (ActionChains(self.page.driver)
         .move_to_element(cpf_input)
         .click()
         .key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL)
         .send_keys(str(format_cpf(cpf)))
         .perform())
        self.page.search_button().click()
        return self

    def search_process_number(self, process_number: str) -> 'PJeAction':
        process_number_input = self.page.process_number_input()

        (ActionChains(self.page.driver)
         .move_to_element(process_number_input)
         .click()
         .key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL)
         .send_keys(str(format_process_number(process_number)))
         .perform())
        self.page.search_button().click()
        return self

    def _wait_row_or_error(self, timeout: int = QUERY_TIMEOUT):
        def _predicate(driver: CustomWebDriver) -> bool:
            has_rows = len(driver.find_element(By.ID, self.page.PROCESS_TABLE).find_elements(By.TAG_NAME, "tr")) > 0
            has_alert = driver.find_elements(By.CLASS_NAME, self.page.ERROR_MESSAGE)
            try:
                return has_rows or (len(has_alert) > 0 and has_alert[0].is_displayed())
            except StaleElementReferenceException:
                return False

        try:
            self.driver().wait_condition(_predicate, timeout=timeout)
        except TimeoutException:
            raise LibJusBrException(f'A consulta está demorando mais do que o esperado, tente novamentes')

        error_message = self.page.error_message_text()
        if error_message:
            raise LibJusBrException(error_message)

    def extract_process_list(self) -> List[SimpleProcessData]:
        self._wait_row_or_error()
        rows = self.page.get_process_rows()
        process_list = []
        for row in rows:
            tds = row.find_elements(By.TAG_NAME, "td")
            process_class, process_details, persons = tds[1].text.split('\n')
            status, status_at = tds[2].text.rsplit('(', maxsplit=1)
            plaintiff, defendant = persons.split(' X ')
            process_number, subject = process_details.split(' - ')
            process_list.append(SimpleProcessData(
                process_class=process_class.strip(),
                process_class_abv=process_number.split(' ')[0].strip(),
                process_number=process_number.split(' ')[1].strip(),
                subject=subject.strip(),
                plaintiff=plaintiff.strip(),
                defendant=defendant.strip(),
                status=status.strip(),
                last_update=to_date_time(
                    status_at.strip().replace('(', '').replace(')', '')
                ),
            ))
        return process_list

    def _extract_process_data(self) -> ProcessData:
        return ProcessData(
            process_number=self.page.process_number(),
            distribution_date=to_date(self.page.distribution_date()),
            jurisdiction=self.page.jurisdiction(),
            judicial_class=self.page.judicial_class(),
            judge_entity=self.page.judge_entity(),
            collegiate_judge_entity=self.page.collegiate_judge_entity(),
            referenced_process_number=self.page.referenced_process_number(),
            subject=self.page.subject(),
        )

    @classmethod
    def _extract_document(cls, doc) -> DocumentParty | None:
        doc = str(doc).upper()
        only_digits_doc = only_digits(doc)
        if 'CPF' in str(doc):
            return DocumentParty.of_cpf(
                doc
                .replace('CPF', '')
                .replace('.', '')
                .replace('-', '')
                .replace(':', '')
                .strip()
            )
        elif 'CNPJ' in str(doc):
            return DocumentParty.of_cnpj(
                doc
                .replace('CNPJ', '')
                .replace('.', '')
                .replace('-', '')
                .replace(':', '')
                .replace('/', '')
                .strip()
            )
        elif 'OAB' in str(doc):
            return DocumentParty.of_oab(doc.replace('OAB', '').strip())
        if only_digits_doc:
            raise LibJusBrException(f'cannot get document for {doc}')
        return None

    @classmethod
    def _extract_parties(cls, elements):
        parties = []
        for party in elements:
            text_content = party.find_element(By.TAG_NAME, 'div').find_element(By.TAG_NAME, 'span').get_attribute(
                'textContent'
            )
            parts = text_content.split(' - ')
            documents = parts[1:len(parts) - 1]
            last_document, role = parts[len(parts) - 1].split(' (')
            documents.append(last_document.strip())

            parties.append(Party(
                name=parts[0].strip(),
                documents=list(filter(lambda x: x is not None, [cls._extract_document(doc) for doc in documents])),
                role=role.replace(')', '').strip()
            ))

        return parties

    def _extract_active_parties(self) -> List[Party]:
        return self._extract_parties(self.page.get_active_party_table_body().find_elements(By.TAG_NAME, 'tr'))

    def _extract_passive_parties(self) -> List[Party]:
        return self._extract_parties(self.page.get_passive_party_table_body().find_elements(By.TAG_NAME, 'tr'))

    def _extract_case_parties(self) -> CaseParty:
        return CaseParty(
            active=self._extract_active_parties(),
            passive=self._extract_passive_parties(),
        )

    @classmethod
    def _extract_movement(cls, el) -> Movement:
        td1, td2 = [x.text for x in el.find_elements(By.TAG_NAME, 'td')]
        created_at, description = td1.split(' - ', maxsplit=1)
        if td2:
            document_date, document_ref = td2.split(' - ', maxsplit=1)
        else:
            document_ref = None
            document_date = None
        return Movement(
            created_at=to_date_time(created_at),
            description=description,
            document_date=to_date_time(
                document_date
            ) if document_date else None,
            document_ref=document_ref,
        )

    def _input_next(self, page_input):
        next_val = int(page_input.get_attribute('value')) + 1
        (ActionChains(self.page.driver)
         .move_to_element(page_input)
         .click()
         .key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL)
         .send_keys(str(next_val))
         .perform())

    def _extract_movements(self) -> List[Movement]:
        movements = []
        quantity = self.page.movements_quantity()

        while len(movements) != quantity:
            rows = self.page.movements_table().find_elements(By.TAG_NAME, 'tr')
            first_row_text = rows[0].find_element(By.TAG_NAME, 'td').text

            movements.extend([self._extract_movement(x) for x in rows])

            if len(movements) == quantity:
                break

            self._input_next(self.page.movements_page_input())

            self.driver().wait_condition(lambda x: _first_row_changed_predicate(
                x, self.page.MOVEMENTS_TABLE_BODY, first_row_text
            ), timeout=20)

        return movements

    def _read_file_remove_and_close(self):
        def _wait_file_predicate(driver: CustomWebDriver):
            return driver.downloads_quantity() > 0

        self.page.driver.wait_condition(_wait_file_predicate)

        file = os.path.join(self.page.driver.download_folder, os.listdir(self.page.driver.download_folder)[0])

        log.info(f'downloaded file {file}')

        with open(file, 'rb') as f:
            file_b64 = base64.b64encode(f.read()).decode('utf-8')

        os.remove(file)
        log.info(f'removed file {file}')

        self.page.close_current_window()
        return file_b64

    def _is_downloadable_window(self, description):
        if 'login' in self.page.driver.current_url:
            log.warning(f'Document {description} needs login to be downloaded')
            return False
        elif 'Denied' in self.page.driver.title:
            log.warning(f'Document {description} access denied')
            return False
        else:
            return True

    def _extract_attachment(self, row_index) -> Attachment:
        row = self.page.attachments_table_body().find_elements(By.TAG_NAME, 'tr')[row_index]
        td1, _ = row.find_elements(By.TAG_NAME, 'td')
        anchor_tag = td1.find_element(By.TAG_NAME, 'a')
        parts = anchor_tag.text.split('\n')[-1].split(' - ')
        date = next((x for x in parts if is_date_time(x)), None)
        parts.remove(date)
        description = ' '.join(parts)
        self.driver().scroll_to(row)

        anchor_tag.click()
        self.page.driver.wait_condition(lambda x: _window_handles_gt_predicate(x, 2))
        self.page.switch_window()

        file_b64 = None
        if self._is_downloadable_window(description):
            try:
                self.page.download_pdf_file().click()
                file_b64 = self._read_file_remove_and_close()
            except TimeoutException:
                # Sometimes the file is downloaded without the click (direct downloads)
                if self.page.driver.downloads_quantity() == 0:
                    log.error(f'failed to download attachment {description}')
                    self.page.close_current_window()
                else:
                    file_b64 = self._read_file_remove_and_close()
        else:
            self.page.close_current_window()

        protocol_b64 = None
        row = self.page.attachments_table_body().find_elements(By.TAG_NAME, 'tr')[row_index]
        _, td2 = row.find_elements(By.TAG_NAME, 'td')

        if len(td2.find_elements(By.TAG_NAME, 'a')) > 0:
            td2.click()
            self.page.driver.wait_condition(lambda x: _window_handles_gt_predicate(x, 2))
            self.page.switch_window()

            if self._is_downloadable_window(description):
                protocol_b64 = self._read_file_remove_and_close()
            else:
                self.page.close_current_window()

        return Attachment(
            created_at=to_date_time(date),
            description=description,
            file_b64=file_b64,
            protocol_b64=protocol_b64,
        )

    def _extract_attachments(self) -> List[Attachment]:
        attachments = []
        quantity = self.page.attachments_quantity()

        while len(attachments) != quantity:
            rows = self.page.attachments_table_body().find_elements(By.TAG_NAME, 'tr')
            rows_quantity = len(rows)
            first_row_text = rows[0].find_element(By.TAG_NAME, 'td').text

            for i in range(rows_quantity):
                attachments.append(self._extract_attachment(i))

            if len(attachments) == quantity:
                break

            self._input_next(self.page.attachments_page_input())
            self.driver().wait_condition(lambda x: _first_row_changed_predicate(
                x, self.page.ATTACHMENTS_TABLE_BODY, first_row_text
            ), timeout=20)
        return attachments

    def extract_detailed_process(self, process_index_or_number: str = 0):
        self._wait_row_or_error()
        row = None
        rows = self.page.get_process_rows()
        if isinstance(process_index_or_number, int):
            if process_index_or_number < len(rows):
                row = rows[process_index_or_number]
        else:
            process_list = self.extract_process_list()
            for i in range(len(process_list)):
                process = process_list[i]
                if only_digits(process.process_number) == only_digits(process_index_or_number):
                    row = rows[process_index_or_number]
                    break

        if row is None:
            raise LibJusBrException(f'cannot find process {process_index_or_number}')

        tds = row.find_elements(By.TAG_NAME, "td")
        tds[0].click()
        self.page.driver.wait_condition(lambda x: _window_handles_gt_predicate(x, 1))

        self.page.switch_window()
        detailed_data = DetailedProcessData(
            process=self._extract_process_data(),
            case_parties=self._extract_case_parties(),
            movements=self._extract_movements(),
            attachments=self._extract_attachments()
        )
        self.page.close_current_window()
        return detailed_data
