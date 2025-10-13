import threading

from lib.webdriver.driver import new_driver

_lock = threading.Lock()
_drivers = {
    'default': new_driver()
}


def get_driver_singleton():
    with _lock:
        return _drivers['default']
