import dataclasses

from lib.exceptions import LibJusBrException
from lib.log_utils import get_logger
from lib.pje.action import PJeAction
from lib.pje.constants import URLS
from lib.pje.page import TRF1PJePage, TRF3PJePage, TRF5PJePage, TRF6PJePage
from lib.pje.types import Grade, TribunalPje
from lib.webdriver.driver import CustomWebDriver
from lib.webdriver.service import Service

logger = get_logger(__name__)


@dataclasses.dataclass(frozen=True)
class PJeService(Service[PJeAction]):
    tribunal: TribunalPje = dataclasses.field()

    def _get_proper_url(self, grade: Grade) -> str:
        try:
            return URLS[self.tribunal][grade]
        except KeyError:
            raise LibJusBrException(f'cannot find PJE Url for tribunal {self.tribunal} and grade {grade}')

    def get_process_list(
            self, term: str, grade: Grade
    ):
        logger.info(f'Starting get simple process data for term {term}')
        self.go_to(self._get_proper_url(grade))
        simple_data = (
            self
            .action
            .enter_site()
            .search_term(term)
            .extract_process_list()
        )
        logger.info(f'Finished get simple process data for term {term}')
        return simple_data

    def get_detailed_process(
            self, term: str, grade: Grade, process_index_or_number: str | int = 0
    ):
        logger.info(f'Starting get detailed process data for term {term}')
        self.go_to(self._get_proper_url(grade))
        data = (
            self
            .action
            .enter_site()
            .search_term(term)
            .extract_detailed_process(process_index_or_number)
        )
        logger.info(f'Finished get detailed process data for term {term}')
        return data


def get_trf1_service(d: CustomWebDriver) -> PJeService:
    return PJeService(
        action=PJeAction(TRF1PJePage(driver=d)),
        tribunal='trf1',
    )


def get_trf3_service(d: CustomWebDriver) -> PJeService:
    return PJeService(
        action=PJeAction(TRF3PJePage(driver=d)),
        tribunal='trf3'
    )


def get_trf5_service(d: CustomWebDriver) -> PJeService:
    return PJeService(
        action=PJeAction(TRF5PJePage(driver=d)),
        tribunal='trf5'
    )


def get_trf6_service(d: CustomWebDriver) -> PJeService:
    return PJeService(
        action=PJeAction(TRF6PJePage(driver=d)),
        tribunal='trf6'
    )
