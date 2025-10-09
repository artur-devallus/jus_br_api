import dataclasses
from typing import Literal

from lib.trf1.action import TRF1Action
from lib.trf1.constants import FIRST_GRADE_URL, SECOND_GRADE_URL
from lib.trf1.page import TRF1Page
from lib.webdriver.driver import CustomWebDriver
from lib.webdriver.service import Service

Grade = Literal['first'] | Literal['second']


@dataclasses.dataclass(frozen=True)
class TRF1Service(Service[TRF1Action]):

    @classmethod
    def _get_proper_url(cls, grade: Grade) -> str:
        return FIRST_GRADE_URL if grade == 'first' else SECOND_GRADE_URL

    def get_simple_process_data(self, cpf: str, grade: Grade = 'first'):
        self.go_to(self._get_proper_url(grade))
        return (
            self
            .action
            .search_cpf(cpf)
            .extract_simple_process_data()
        )


def get_trf1_service(d: CustomWebDriver) -> TRF1Service:
    return TRF1Service(TRF1Action(TRF1Page(driver=d)))
