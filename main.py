import dataclasses
import json
import logging

from lib.json_utils import default_json_encoder
from lib.pje.service import get_pje_service
from lib.webdriver.driver import new_driver

logging.basicConfig(level=logging.INFO)

CPF = '37626361334'

if __name__ == '__main__':
    with new_driver(
            headless=True
    ) as driver:

        with open(f'{CPF}.json', 'w') as f:
            data = get_pje_service(driver).get_detailed_process_data(cpf=CPF)

            json_data = dataclasses.asdict(data)
            logging.info(json.dumps(json_data, indent=2, default=default_json_encoder))
            json.dump(json_data, f, indent=2, default=default_json_encoder)

        # print(service.get_simple_process_data(cpf='05213730345'))
