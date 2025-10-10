import dataclasses
import json
import logging

from lib.json_utils import default_json_encoder
from lib.pje.service import get_trf3_service, get_trf5_service, get_trf6_service
from lib.eproc.service import get_trf6_service
from lib.webdriver.driver import new_driver

logging.basicConfig(level=logging.INFO)

NOT_FOUND_CPF = '02382814349'

CPF_TRF1 = '37626361334'
PROCESS_NUMBER_TRF1 = '0005141-10.2015.4.01.0000'

PROCESS_NUMBER_TRF3 = '00035473620174036110'
CPF_TRF3 = '06013333815'

CPF_TRF5 = '032.778.684-19'
PROCESS_NUMBER_TRF5 = '08042016320204058200'

CPF_TRF6 = '009.983.386-72'
PROCESS_NUMBER_TRF6 = '0052515-05.2014.4.01.3800'

CPF_TRF2 = '001.286.587-70'
PROCESS_NUMBER_TRF2 = '0004484-12.2013.4.02.0000'

if __name__ == '__main__':
    term = CPF_TRF6
    with new_driver(
            headless=False
    ) as driver:
        data = get_trf6_service(driver).get_process_list(
            term=term, grade='eproc1g'
        )

        json_data = dataclasses.asdict(data)
        logging.info(json.dumps(json_data, indent=2, default=default_json_encoder))
        with open(f'pje_{term}.json', 'w') as f:
            json.dump(json_data, f, indent=2, default=default_json_encoder)
