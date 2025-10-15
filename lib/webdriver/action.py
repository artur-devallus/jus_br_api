import base64
import dataclasses
import hashlib
import os
from typing import TypeVar, Generic

from lib.webdriver.driver import CustomWebDriver
from lib.webdriver.page import Page

T = TypeVar('T', bound=Page)


@dataclasses.dataclass(frozen=True)
class Action(Generic[T]):
    page: T = dataclasses.field()

    def driver(self):
        return self.page.driver

    def go_to(self, url):
        self.page.go_to(url)

    @classmethod
    def read_md5(cls, f_bytes):
        return hashlib.md5(f_bytes).hexdigest()

    def read_file_remove_and_close(self):
        def _wait_file_predicate(driver: CustomWebDriver):
            return driver.downloads_quantity() > 0

        self.page.driver.wait_condition(_wait_file_predicate)

        file = os.path.join(self.page.driver.download_folder, os.listdir(self.page.driver.download_folder)[0])

        with open(file, 'rb') as f:
            f_bytes = f.read()
            file_b64 = base64.b64encode(f_bytes).decode('utf-8')
            md5 = self.read_md5(f_bytes)

        os.remove(file)

        self.page.close_current_window()
        return file_b64, md5
