import os

WEBDRIVER_BASE_PATH = os.getenv('WEBDRIVER_BASE_PATH', '/tmp')
HEADLESS = bool(int(os.getenv('HEADLESS', '1')))
CHROME_BINARY = os.getenv('CHROME_BINARY', '/opt/google/chrome/chrome')
CHROMEDRIVER_PATH = os.getenv('CHROMEDRIVER_PATH', '/opt/chromedriver/chromedriver')
PAGE_LOAD_TIMEOUT = int(os.getenv('PAGE_LOAD_TIMEOUT', '60'))
DEFAULT_TIMEOUT = int(os.getenv('DEFAULT_TIMEOUT', '5'))
PROXY = bool(int(os.getenv('PROXY', '0')))
DEFALT_CHROME_AGENT = (
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'
)
