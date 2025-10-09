import logging

from lib.trf1.service import get_trf1_service
from lib.webdriver.driver import new_driver

logging.basicConfig(level=logging.INFO)
if __name__ == '__main__':
    with new_driver(
            headless=False
    ) as driver:
        service = get_trf1_service(driver)

        print(service.get_detailed_process_data(cpf='37626361334'))
        # print(service.get_simple_process_data(cpf='05213730345'))

