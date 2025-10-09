import dataclasses

from lib.webdriver.driver import CustomWebDriver


@dataclasses.dataclass(frozen=True)
class Page:
    driver: CustomWebDriver = dataclasses.field()
    initial_url: str = dataclasses.field(default=None)
    skip_load: bool = dataclasses.field(default=False)

    def __post_init__(self):
        if not self.skip_load and self.initial_url:
            self.driver.get(self.initial_url)

    def go_to(self, url: str):
        self.driver.get(url)
