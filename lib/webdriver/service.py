import abc
import dataclasses
from typing import TypeVar, Generic

from lib.webdriver.action import Action

T = TypeVar("T", bound=Action)


@dataclasses.dataclass(frozen=True)
class Service(Generic[T], metaclass=abc.ABCMeta):
    action: T = dataclasses.field()

    def go_to(self, url):
        self.action.go_to(url)
