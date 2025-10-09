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

    def switch_window(self):
        next_window = self.driver.window_handles.index(self.driver.current_window_handle) + 1
        if next_window >= len(self.driver.window_handles):
            next_window = 0
        self.driver.switch_to.window(self.driver.window_handles[next_window])

    def close_current_window(self):
        if len(self.driver.window_handles) == 1:
            return
        current = self.driver.current_window_handle
        other = [x for x in self.driver.window_handles if x != current]
        self.driver.close()
        self.driver.switch_to.window(other[0])
