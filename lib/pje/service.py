import dataclasses
import logging
from typing import Literal

from lib.pje.action import PJeAction
from lib.pje.constants import FIRST_GRADE_URL, SECOND_GRADE_URL
from lib.pje.page import PJePage
from lib.webdriver.driver import CustomWebDriver
from lib.webdriver.service import Service

Tribunal = Literal['trf1'] | Literal['trf3'] | Literal['trf4'] | Literal['trf5'] | Literal['trf6']
Grade = Literal['first'] | Literal['second']
logger = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True)
class PJeService(Service[PJeAction]):
    @classmethod
    def _get_proper_url(cls, tribunal: Tribunal, grade: Grade) -> str:
        return (FIRST_GRADE_URL if grade == 'first' else SECOND_GRADE_URL).format(tribunal=tribunal)

    def get_simple_process_data(self, cpf: str, tribunal: Tribunal = 'trf1', grade: Grade = 'first'):
        logger.info(f'Starting get simple process data for cpf {cpf}')
        self.go_to(self._get_proper_url(tribunal, grade))
        simple_data = (
            self
            .action
            .search_cpf(cpf)
            .extract_simple_process_data()
        )
        logger.info(f'Finished get simple process data for cpf {cpf}')
        return simple_data

    def get_detailed_process_data(self, cpf: str, tribunal: Tribunal = 'trf1', grade: Grade = 'first'):
        logger.info(f'Starting get detailed process data for cpf {cpf}')
        self.go_to(self._get_proper_url(tribunal, grade))
        data = (
            self
            .action
            .search_cpf(cpf)
            .extract_detailed_process_data()
        )
        logger.info(f'Finished get detailed process data for cpf {cpf}')
        return data


def get_pje_service(d: CustomWebDriver) -> PJeService:
    return PJeService(PJeAction(PJePage(driver=d)))
