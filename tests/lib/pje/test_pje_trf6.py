import dataclasses
import json
import unittest

from lib.json_utils import default_json_encoder
from lib.pje.service import get_trf6_service
from lib.webdriver.driver import new_driver



class TestTrf6(unittest.TestCase):
    def setUp(self):
        self.driver = new_driver()

    def tearDown(self):
        self.driver.quit()

    def test_trf3_get_detailed_data_for_cpf_98470702(self):
        detailed_data = get_trf6_service(self.driver).get_detailed_process(
            term='02598470702',
            grade='pje1g',
        )

        print(json.dumps(dataclasses.asdict(detailed_data), indent=2, default=default_json_encoder))
