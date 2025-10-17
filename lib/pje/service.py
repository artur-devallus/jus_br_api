import dataclasses
from typing import List

from lib.exceptions import LibJusBrException
from lib.log_utils import get_logger
from lib.models import DetailedProcessData
from lib.pje.action import PJeAction
from lib.pje.constants import URLS
from lib.pje.page import TRF1PJePage, TRF3PJePage, TRF6PJePage
from lib.pje.types import Grade, TribunalPje
from lib.webdriver.driver import CustomWebDriver
from lib.webdriver.service import Service

logger = get_logger(__name__)


@dataclasses.dataclass(frozen=True)
class PJeService(Service[PJeAction]):
    tribunal: TribunalPje = dataclasses.field()
    grade: Grade = dataclasses.field()

    def __post_init__(self):
        if self.grade:
            self.go_to(self._get_proper_url())

    def _get_proper_url(self, ) -> str:
        try:
            return URLS[self.tribunal][self.grade]
        except KeyError:
            raise LibJusBrException(f'cannot find PJE Url for tribunal {self.tribunal} and grade {self.grade}')

    def get_process_list(
            self, term: str,
    ):
        logger.info(f'Starting get simple process data for term {term}')
        simple_data = (
            self
            .action
            .enter_site()
            .search_term(term)
            .extract_process_list()
        )
        logger.info(f'Finished get simple process data for term {term}')
        return simple_data

    def get_detailed_processes(
            self, term: str,
    ) -> List[DetailedProcessData]:
        logger.info(f'Starting get detailed process data for term {term}')
        data = (
            self
            .action
            .enter_site()
            .search_term(term)
            .extract_all()
        )
        logger.info(f'Finished get detailed process data for term {term}')
        return data


def get_trf1_service(d: CustomWebDriver, grade: Grade = 'pje1g') -> PJeService:
    return PJeService(
        action=PJeAction(TRF1PJePage(driver=d)),
        tribunal='trf1',
        grade=grade
    )


def get_trf3_service(d: CustomWebDriver, grade: Grade = 'pje1g') -> PJeService:
    return PJeService(
        action=PJeAction(TRF3PJePage(driver=d)),
        tribunal='trf3',
        grade=grade
    )


def get_trf6_service(d: CustomWebDriver, grade: Grade = 'pje1g') -> PJeService:
    return PJeService(
        action=PJeAction(TRF6PJePage(driver=d)),
        tribunal='trf6',
        grade=grade
    )


def get_action_for_tribunal(tribunal: TribunalPje, driver):
    if tribunal == 'trf1':
        return PJeAction(TRF1PJePage(driver=driver))
    elif tribunal == 'trf3':
        return PJeAction(TRF3PJePage(driver=driver))
    elif tribunal == 'trf6':
        return PJeAction(TRF6PJePage(driver=driver))
    raise LibJusBrException(f'cannot get PJe Service for tribunal {tribunal}')


def get_pje_service_for_tribunal(
        tribunal: TribunalPje, driver: CustomWebDriver, grade: Grade
) -> PJeService:
    return PJeService(get_action_for_tribunal(tribunal=tribunal, driver=driver), tribunal, grade)
