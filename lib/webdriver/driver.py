import os
import shutil
import time
from tempfile import mkdtemp
from typing import Any, Callable, List

from selenium import webdriver
from selenium.common import StaleElementReferenceException, JavascriptException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from selenium_stealth import stealth

from lib.log_utils import get_logger
from lib.webdriver.constants import (
    HEADLESS, WEBDRIVER_BASE_PATH, CHROME_BINARY,
    CHROMEDRIVER_PATH, PAGE_LOAD_TIMEOUT, DEFAULT_TIMEOUT, PROXY, DEFALT_CHROME_AGENT
)

log = get_logger('chrome_driver')


def _window_handles_gt_predicate(driver, expected_len):
    return len(driver.window_handles) > expected_len


class CustomWebDriver(WebDriver):
    def __init__(self, options, service, download_folder, base_folder):
        super().__init__(options, service)
        self.options = options
        self.download_folder = download_folder
        self.base_folder = base_folder
        log.info(f'new driver has launched pid={self.service.process.pid}')

    def remove_folder(self):
        try:
            if os.path.exists(self.download_folder):
                shutil.rmtree(self.download_folder, ignore_errors=True)
        except AttributeError:
            ...
        try:
            if os.path.exists(self.base_folder):
                shutil.rmtree(self.base_folder, ignore_errors=True)
        except AttributeError:
            ...

    def close(self) -> None:
        super().close()

    def quit(self) -> None:
        self.remove_folder()
        chrome_pid = self.service.process.pid
        try:
            super().quit()
        finally:
            try:
                self.service.stop()
            except Exception:
                pass
            if chrome_pid:
                os.system(f"pkill -P {chrome_pid} || true")

        log.info(f'driver closed pid={self.service.process.pid}')

    def __exit__(self, *args, **kwargs):
        self.quit()

    def __enter__(self):
        return self

    def scroll_to(self, element: WebElement):
        self.execute_script('arguments[0].scrollIntoViewIfNeeded(true);', element)

    @classmethod
    def wait(cls, amount):
        time.sleep(amount)

    def wait_windows_greather_than(self, windows_size):
        return self.wait_condition(lambda x: _window_handles_gt_predicate(x, windows_size))

    def wait_condition(self, condition: Any, timeout: int = DEFAULT_TIMEOUT) -> WebElement:
        return WebDriverWait(self, timeout=timeout).until(condition)

    def wait_presence(self, by: str, val: str, timeout: int = DEFAULT_TIMEOUT) -> WebElement:
        return self.wait_condition(ec.presence_of_element_located(
            (by, val)
        ), timeout)

    def wait_visibility(self, by: str, val: str, timeout: int = DEFAULT_TIMEOUT) -> WebElement:
        def _predicate(driver: CustomWebDriver) -> bool:
            try:
                el = driver.find_element(by, val)
                return el and el.is_displayed() == True
            except (StaleElementReferenceException, JavascriptException):
                return False

        return self.wait_condition(_predicate, timeout)

    def wait_invisibility(self, by: str, val: str, timeout: int = DEFAULT_TIMEOUT) -> WebElement:
        def _predicate(driver: CustomWebDriver) -> bool:
            try:
                el = driver.find_element(by, val)
                return el and el.is_displayed() == False
            except (StaleElementReferenceException, JavascriptException):
                return False

        return self.wait_condition(_predicate, timeout)

    def wait_visibility_id(self, val: str, timeout: int = DEFAULT_TIMEOUT) -> WebElement:
        return self.wait_visibility(By.ID, val, timeout)

    def wait_invisibility_id(self, val: str, timeout: int = DEFAULT_TIMEOUT) -> WebElement:
        return self.wait_invisibility(By.ID, val, timeout)

    def wait_clickable(self, by: str, val: str, timeout: int = DEFAULT_TIMEOUT) -> WebElement:
        return self.wait_condition(ec.element_to_be_clickable(
            (by, val)
        ), timeout)

    def wait_clickable_id(self, val: str, timeout: int = DEFAULT_TIMEOUT) -> WebElement:
        return self.wait_clickable(By.ID, val, timeout)

    def wait_clickable_xpath(self, val: str, timeout: int = DEFAULT_TIMEOUT) -> WebElement:
        return self.wait_clickable(By.XPATH, val, timeout)

    def wait_clickable_name(self, val: str, timeout: int = DEFAULT_TIMEOUT) -> WebElement:
        return self.wait_clickable(By.NAME, val, timeout)

    def wait_presence_id(self, val: str, timeout: int = DEFAULT_TIMEOUT) -> WebElement:
        return self.wait_presence(By.ID, val, timeout)

    def find_by(self, by, val, timeout: int = DEFAULT_TIMEOUT) -> WebElement:
        self.wait_presence(by, val, timeout)
        return self.find_element(by, val)

    def find_by_id(self, val: str, timeout: int = DEFAULT_TIMEOUT) -> WebElement:
        return self.find_by(By.ID, val, timeout)

    def find_by_class_name(self, val: str, timeout: int = DEFAULT_TIMEOUT) -> WebElement:
        return self.find_by(By.CLASS_NAME, val, timeout)

    def find_all_by_class_name(self, val: str) -> List[WebElement]:
        return self.find_elements(By.CLASS_NAME, val)

    def find_by_tag_name(self, val: str, timeout: int = DEFAULT_TIMEOUT) -> WebElement:
        return self.find_by(By.TAG_NAME, val, timeout)

    def find_by_xpath(self, val: str, timeout: int = DEFAULT_TIMEOUT) -> WebElement:
        return self.find_by(By.XPATH, val, timeout)

    def find_by_name(self, val: str, timeout: int = DEFAULT_TIMEOUT) -> WebElement:
        return self.find_by(By.NAME, val, timeout)

    def wait_until_input_value_by_id(self, el_id: str, value: Any) -> WebElement:
        def _predicate(driver: CustomWebDriver) -> bool:
            return str(driver.find_by_id(el_id).get_attribute('value')) == str(value)

        return self.wait_condition(_predicate)

    def wait_until_input_value(self, by: str, by_el: str, value: Any) -> WebElement:
        def is_value(x):
            current_val = str(x.find_by(by, by_el).get_attribute('value'))
            is_val = False
            set_val = ''
            if isinstance(value, str):
                expected_value = str(value)
                is_val = current_val == expected_value
            elif isinstance(value, list):
                is_val = current_val in value
                set_val = value[0]

            if is_val:
                return is_val
            x.find_by(by, by_el).click()
            x.find_by(by, by_el).send_keys(set_val)
            return is_val

        return self.wait_condition(
            is_value
        )

    def empty_and_set_value(
            self,
            input_f: Callable[[], WebElement],
            input_id: str,
            value: Any,
            expected_values: Any = None,
            input_by: str = By.ID,
            empty: bool = True,
    ):
        if not expected_values:
            values = [str(value)]
        else:
            values = expected_values
        if empty:
            input_el = input_f()
            input_el.clear()
            self.wait_until_input_value(input_by, input_id, '')
        input_el = input_f()
        input_el.click()
        input_el.send_keys(str(value))
        self.wait_until_input_value(input_by, input_id, values)

    def screenshot(self) -> str:
        return self.get_screenshot_as_base64()

    def find_iframes(self, required_count: int = 1):
        self.wait_condition(
            lambda x: len(x.find_elements(By.TAG_NAME, 'iframe')) == required_count
        )
        return self.find_elements(By.TAG_NAME, 'iframe')

    def wait_dom_ready(self):
        self.wait_condition(
            lambda x: x.execute_script("return document.readyState") == "complete"
        )

    def downloads_quantity(self):
        list_files = os.listdir(self.download_folder)
        download_count = 0
        for download_file in list_files:
            if not download_file.endswith('.crdownload'):
                download_count += 1
        return download_count

    def is_headless(self):
        return '--headless=new' in self.options.arguments


def new_driver(
        headless: bool = HEADLESS,
        proxy: bool = PROXY,
        base_folder: str = None
) -> CustomWebDriver:
    options = webdriver.ChromeOptions()
    if base_folder is None:
        base_folder = mkdtemp(dir=WEBDRIVER_BASE_PATH)
    download_folder = os.path.join(base_folder, 'downloads')
    os.makedirs(download_folder, exist_ok=True)

    prefs = {
        'download.prompt_for_download': False,
        'download.default_directory': download_folder,
        'download.directory_upgrade': True,
        'plugins.always_open_pdf_externally': True,
    }

    if headless:
        options.add_argument('--headless=new')

    proxy_server = '14.251.13.0:8080'
    options.add_argument('--no-sandbox')
    if proxy:
        options.add_argument(f'--proxy-server={proxy_server}')

    options.add_argument('--disable-gpu')
    options.add_argument('--disable-extensions')
    options.add_argument('--window-size=1366,768')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-dev-tools')
    options.add_argument("--dns-prefetch-disable")
    options.add_argument(f'--user-data-dir={base_folder}')
    options.add_argument(f'--data-path={base_folder}')
    options.add_argument(f'--disk-cache-dir={base_folder}')
    options.add_argument('--disable-browser-side-navigation')
    options.add_argument('--no-zygote')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument("--disable-features=NetworkPrediction,Prefetch")
    options.add_argument("--disable-blink-features=Prefetch")
    options.add_argument("--disable-background-networking")
    options.add_argument("--disable-prerender-from-omnibox")
    options.add_argument(f'--user-agent={DEFALT_CHROME_AGENT}')

    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)

    if CHROME_BINARY:
        options.binary_location = CHROME_BINARY

    chromedriver_path = CHROMEDRIVER_PATH
    options.add_experimental_option('prefs', prefs)

    if chromedriver_path is None:
        raise RuntimeError('Not implemented')
    driver = CustomWebDriver(
        service=Service(executable_path=chromedriver_path),
        options=options,
        base_folder=base_folder,
        download_folder=download_folder,
    )
    driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
    driver.execute_cdp_cmd('Page.setDownloadBehavior', {
        'behavior': 'allow',
        'downloadPath': download_folder,
    })
    driver.maximize_window()
    driver.set_window_rect(x=0, y=0, width=1366, height=768)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    l: Any = ["pt-BR", 'pt']
    stealth(
        driver,
        languages=l,
        vendor='Google Inc.',
        platform='Win64',
        webgl_vendor='Intel Inc.',
        renderer='Intel Iris OpenGL Engine',
        fix_hairline=True,
    )
    return driver
