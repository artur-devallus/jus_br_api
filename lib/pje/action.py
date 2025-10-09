import base64
import dataclasses
import datetime
import os
from typing import List

from selenium.common import StaleElementReferenceException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By

from lib.cpf_utils import format_cpf
from lib.exceptions import LibJusBrException
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
from lib.pje.page import PJePage
from lib.string_utils import only_digits
from lib.webdriver.action import Action
from lib.webdriver.driver import CustomWebDriver


@dataclasses.dataclass(frozen=True)
class PJeAction(Action[PJePage]):

    def search_cpf(self, cpf: str) -> 'PJeAction':
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
            try:
                return has_rows or (has_alert and has_alert.is_displayed())
            except StaleElementReferenceException:
                return False

        self.driver().wait_condition(_predicate, timeout=20)

        if self.page.error_message() and self.page.error_message().is_displayed():
            raise LibJusBrException(self.page.error_message().text)

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

    def _extract_process_data(self) -> ProcessData:
        return ProcessData(
            process_number=self.page.process_number(),
            distribution_date=datetime.datetime.strptime(self.page.distribution_date(), '%d/%m/%Y').date(),
            jurisdiction=self.page.jurisdiction(),
            judicial_class=self.page.judicial_class(),
            judge_entity=self.page.judge_entity(),
            subject=self.page.subject(),
        )

    @classmethod
    def _extract_document(cls, doc) -> DocumentParty:
        doc = str(doc).upper()
        if 'CPF' in str(doc):
            return DocumentParty.of_cpf(only_digits(doc))
        elif 'CNPJ' in str(doc):
            return DocumentParty.of_cnpj(only_digits(doc))
        elif 'OAB' in str(doc):
            return DocumentParty.of_oab(doc.replace('OAB', '').strip())
        raise LibJusBrException(f'cannot get document for {doc}')

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
                documents=[cls._extract_document(doc) for doc in documents],
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
            created_at=datetime.datetime.strptime(created_at, '%d/%m/%Y %H:%M:%S'),
            description=description,
            document_date=datetime.datetime.strptime(
                document_date, '%d/%m/%Y %H:%M:%S'
            ) if document_date else None,
            document_ref=document_ref,
        )

    def _extract_movements(self) -> List[Movement]:
        movements = []
        quantity = self.page.movements_quantity()

        while len(movements) != quantity:
            rows = self.page.movements_table().find_elements(By.TAG_NAME, 'tr')
            first_row_text = rows[0].find_element(By.TAG_NAME, 'td').text

            def _first_row_changed_predicate(driver):
                try:
                    current_text = driver.find_element(
                        By.ID, self.page.MOVEMENTS_TABLE_BODY
                    ).find_elements(By.TAG_NAME, 'tr')[0].find_element(
                        By.TAG_NAME, 'td'
                    ).text
                    return first_row_text != current_text
                except StaleElementReferenceException:
                    return False

            movements.extend([self._extract_movement(x) for x in rows])

            if len(movements) == quantity:
                break

            page_input = self.page.movements_page_input()
            next_val = int(page_input.get_attribute('value')) + 1
            (ActionChains(self.page.driver)
             .move_to_element(page_input)
             .click()
             .key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL)
             .send_keys(str(next_val))
             .perform())

            self.driver().wait_condition(_first_row_changed_predicate, timeout=20)

        return movements

    def _read_file_remove_and_close(self):
        def _wait_file_predicate(driver: CustomWebDriver):
            list_files = os.listdir(driver.download_folder)
            for download_file in list_files:
                if download_file.endswith('.crdownload'):
                    return False
            return len(list_files) > 0

        self.page.driver.wait_condition(_wait_file_predicate)

        file = os.path.join(self.page.driver.download_folder, os.listdir(self.page.driver.download_folder)[0])

        with open(file, 'rb') as f:
            file_b64 = base64.b64encode(f.read()).decode('utf-8')
        os.remove(file)

        self.page.close_current_window()
        return file_b64

    def _extract_attachments(self) -> List[Attachment]:
        attachments = []
        rows = self.page.attachments_table_body().find_elements(By.TAG_NAME, 'tr')

        def _wait_window_predicate(driver: CustomWebDriver):
            return len(driver.window_handles) > 2

        for row in rows:
            td1, td2 = row.find_elements(By.TAG_NAME, 'td')
            anchor_tag = td1.find_element(By.TAG_NAME, 'a')
            date, description = anchor_tag.text.split('\n')[1].split(' - ', maxsplit=1)
            self.driver().scroll_to(row)

            # Download the file
            anchor_tag.click()
            self.page.driver.wait_condition(_wait_window_predicate)

            self.page.switch_window()
            self.page.download_pdf_file().click()
            file_b64 = self._read_file_remove_and_close()

            # Download the protocol
            td2.click()
            self.page.driver.wait_condition(_wait_window_predicate)
            self.page.switch_window()
            protocol_b64 = self._read_file_remove_and_close()

            attachments.append(Attachment(
                created_at=datetime.datetime.strptime(date, '%d/%m/%Y %H:%M:%S'),
                description=description,
                file_b64=file_b64,
                protocol_b64=protocol_b64,
            ))
        return attachments

    def extract_detailed_process_data(self):
        def _wait_window_predicate(driver: CustomWebDriver):
            return len(driver.window_handles) > 1

        self._wait_row_or_error()
        row = self.page.get_process_row()
        tds = row.find_elements(By.TAG_NAME, "td")
        tds[0].click()
        self.page.driver.wait_condition(_wait_window_predicate)

        self.page.switch_window()
        detailed_data = DetailedProcessData(
            process=self._extract_process_data(),
            case_parties=self._extract_case_parties(),
            movements=self._extract_movements(),
            attachments=self._extract_attachments()
        )
        self.page.close_current_window()
        return detailed_data
