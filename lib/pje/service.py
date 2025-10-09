import dataclasses

from lib.exceptions import LibJusBrException
from lib.log_utils import get_logger
from lib.pje.action import PJeAction
from lib.pje.constants import URLS
from lib.pje.page import TR1PJePage, TR3PJePage
from lib.pje.types import Grade, Tribunal
from lib.webdriver.driver import CustomWebDriver
from lib.webdriver.service import Service

logger = get_logger(__name__)


@dataclasses.dataclass(frozen=True)
class PJeService(Service[PJeAction]):
    tribunal: Tribunal = dataclasses.field()

    def _get_proper_url(self, grade: Grade) -> str:
        try:
            return URLS[self.tribunal][grade]
        except KeyError:
            raise LibJusBrException(f'cannot find PJE Url for tribunal {self.tribunal} and grade {grade}')

    def get_simple_process_data(
            self, term: str, grade: Grade
    ):
        logger.info(f'Starting get simple process data for term {term}')
        self.go_to(self._get_proper_url(grade))
        simple_data = (
            self
            .action
            .search_term(term)
            .extract_simple_process_data()
        )
        logger.info(f'Finished get simple process data for term {term}')
        return simple_data

    def get_detailed_process_data(
            self, term: str, grade: Grade
    ):
        logger.info(f'Starting get detailed process data for term {term}')
        self.go_to(self._get_proper_url(grade))
        data = (
            self
            .action
            .search_term(term)
            .extract_detailed_process_data()
        )
        logger.info(f'Finished get detailed process data for term {term}')
        return data


def get_trf1_service(d: CustomWebDriver) -> PJeService:
    return PJeService(
        action=PJeAction(TR1PJePage(driver=d)),
        tribunal='trf1',
    )


def get_trf3_service(d: CustomWebDriver) -> PJeService:
    return PJeService(
        action=PJeAction(TR3PJePage(driver=d)),
        tribunal='trf3'
    )
