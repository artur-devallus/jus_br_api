import threading

from lib.webdriver.driver import new_driver

_lock = threading.Lock()
_drivers = {}
KEY_DRIVER = 'main'


def get_driver_singleton():
    with _lock:
        if _drivers.get(KEY_DRIVER):
            return _drivers[KEY_DRIVER]
        driver = new_driver()
        _drivers[KEY_DRIVER] = driver
        return driver
