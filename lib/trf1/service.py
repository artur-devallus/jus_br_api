import dataclasses
import logging
from typing import Literal

from lib.trf1.action import TRF1Action
from lib.trf1.constants import FIRST_GRADE_URL, SECOND_GRADE_URL
from lib.trf1.page import TRF1Page
from lib.webdriver.driver import CustomWebDriver
from lib.webdriver.service import Service

Grade = Literal['first'] | Literal['second']
logger = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True)
class TRF1Service(Service[TRF1Action]):
    @classmethod
    def _get_proper_url(cls, grade: Grade) -> str:
        return FIRST_GRADE_URL if grade == 'first' else SECOND_GRADE_URL

    def get_simple_process_data(self, cpf: str, grade: Grade = 'first'):
        logger.info(f'Starting get simple process data for cpf {cpf}')
        self.go_to(self._get_proper_url(grade))
        simple_data = (
            self
            .action
            .search_cpf(cpf)
            .extract_simple_process_data()
        )
        logger.info(f'Finished get simple process data for cpf {cpf}')
        return simple_data

    def get_detailed_process_data(self, cpf: str, grade: Grade = 'first'):
        logger.info(f'Starting get detailed process data for cpf {cpf}')
        self.go_to(self._get_proper_url(grade))
        data = (
            self
            .action
            .search_cpf(cpf)
            .extract_detailed_process_data()
        )
        logger.info(f'Finished get detailed process data for cpf {cpf}')
        return data


def get_trf1_service(d: CustomWebDriver) -> TRF1Service:
    return TRF1Service(TRF1Action(TRF1Page(driver=d)))
