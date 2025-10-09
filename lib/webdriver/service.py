import abc
import dataclasses
from typing import TypeVar, Generic

from lib.log_utils import get_logger
from lib.webdriver.action import Action

T = TypeVar("T", bound=Action)

log = get_logger(__name__)


@dataclasses.dataclass(frozen=True)
class Service(Generic[T], metaclass=abc.ABCMeta):
    action: T = dataclasses.field()

    def go_to(self, url):
        log.info(f'using url: {url}')
        self.action.go_to(url)
