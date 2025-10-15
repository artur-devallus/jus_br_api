import dataclasses

from lib.log_utils import get_logger
from lib.trf5.action import TRF5Action
from lib.trf5.constants import URL
from lib.trf5.page import TRF5Page
from lib.webdriver.driver import CustomWebDriver
from lib.webdriver.service import Service

logger = get_logger(__name__)


@dataclasses.dataclass(frozen=True)
class TRF5Service(Service[TRF5Action]):

    def get_process_list(
            self, term: str
    ):
        logger.info(f'Starting get simple process data for term {term}')
        self.go_to(URL)
        simple_data = (
            self
            .action
            .search_term(term)
            .get_process_list()
        )
        logger.info(f'Finished get simple process data for term {term}')
        return simple_data

    def get_detailed_process(
            self, term: str, process_index_or_number: str | int = 0
    ):
        logger.info(f'Starting get detailed process data for term {term}')
        self.go_to(URL)
        data = (
            self
            .action
            .search_term(term)
            .get_detailed_process(process_index_or_number)
        )
        logger.info(f'Finished get detailed process data for term {term}')
        return data


def get_trf5_service(d: CustomWebDriver) -> TRF5Service:
    return TRF5Service(
        action=TRF5Action(TRF5Page(driver=d)),
    )
