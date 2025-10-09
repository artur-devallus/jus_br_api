from lib.trf1.service import get_trf1_service
from lib.webdriver.driver import new_driver

if __name__ == '__main__':
    with new_driver(
            headless=True
    ) as driver:
        service = get_trf1_service(driver)

        data = service.get_simple_process_data(cpf='37626361334')
        print(data)
