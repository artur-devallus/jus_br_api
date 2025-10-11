import threading

from lib.webdriver.driver import new_driver

_lock = threading.Lock()
_drivers = {}


def get_driver_singleton_for(tribunal: str):
    with _lock:
        if tribunal in _drivers:
            return _drivers[tribunal]
        driver = new_driver()
        _drivers[tribunal] = driver
        return driver
