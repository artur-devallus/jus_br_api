import dataclasses

from lib.eproc.action import EprocAction
from lib.eproc.constants import URLS
from lib.eproc.page import EprocPage
from lib.eproc.types import TribunalEproc, Grade
from lib.exceptions import LibJusBrException
from lib.log_utils import get_logger
from lib.webdriver.driver import CustomWebDriver
from lib.webdriver.service import Service

logger = get_logger(__name__)


@dataclasses.dataclass(frozen=True)
class EprocService(Service[EprocAction]):
    tribunal: TribunalEproc = dataclasses.field()

    def _get_proper_url(self, grade: Grade) -> str:
        try:
            if isinstance(URLS[self.tribunal], str):
                return URLS[self.tribunal]
            return URLS[self.tribunal][grade]
        except KeyError:
            raise LibJusBrException(f'cannot find Eproc Url for tribunal {self.tribunal} and grade {grade}')

    def get_process_list(
            self, term: str, grade: Grade
    ):
        logger.info(f'Starting get simple process data for term {term}')
        self.go_to(self._get_proper_url(grade))
        simple_data = (
            self
            .action
            .search_term(term)
            .get_process_list()
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
            .search_term(term)
            .get_detailed_process(process_index_or_number)
        )
        logger.info(f'Finished get detailed process data for term {term}')
        return data


def get_trf2_service(d: CustomWebDriver) -> EprocService:
    return EprocService(
        action=EprocAction(EprocPage(driver=d)),
        tribunal='trf2',
    )


def get_trf6_service(d: CustomWebDriver) -> EprocService:
    return EprocService(
        action=EprocAction(EprocPage(driver=d)),
        tribunal='trf6'
    )
