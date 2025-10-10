import dataclasses
import json
import logging

from lib.json_utils import default_json_encoder
from lib.pje.service import get_trf3_service
from lib.webdriver.driver import new_driver

logging.basicConfig(level=logging.INFO)

CPF = '37626361334'
PROCESS_NUMBER = '0005141-10.2015.4.01.0000'
PROCESS_NUMBER_2 = '00035473620174036110'

if __name__ == '__main__':
    term = PROCESS_NUMBER_2
    with new_driver(
            headless=False
    ) as driver:
        data = get_trf3_service(driver).get_detailed_process(
            term=term, grade='pje1g'
        )

        json_data = dataclasses.asdict(data)
        logging.info(json.dumps(json_data, indent=2, default=default_json_encoder))
        with open(f'pje_{term}.json', 'w') as f:
            json.dump(json_data, f, indent=2, default=default_json_encoder)
