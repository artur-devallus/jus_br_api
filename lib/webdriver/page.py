import dataclasses

from lib.webdriver.driver import CustomWebDriver


@dataclasses.dataclass(frozen=True)
class Page:
    driver: CustomWebDriver = dataclasses.field()

    def go_to(self, url: str):
        self.driver.get(url)

    def switch_window(self):
        index_next = self.driver.window_handles.index(self.driver.current_window_handle) + 1
        if index_next >= len(self.driver.window_handles):
            index_next = 0

        next_window = self.driver.window_handles[index_next]
        self.driver.switch_to.window(next_window)
        self.driver.wait_condition(lambda x: x.current_window_handle == next_window)

    def close_current_window(self):
        if len(self.driver.window_handles) == 1:
            return
        current = self.driver.current_window_handle
        other = [x for x in self.driver.window_handles if x != current]
        self.driver.close()
        self.driver.switch_to.window(other[-1])
