import dataclasses
from typing import TypeVar, Generic

from lib.webdriver.page import Page

T = TypeVar('T', bound=Page)


@dataclasses.dataclass(frozen=True)
class Action(Generic[T]):
    page: T = dataclasses.field()

    def driver(self):
        return self.page.driver

    def go_to(self, url):
        self.page.go_to(url)
