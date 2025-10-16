import dataclasses
import json
import unittest

from lib.exceptions import LibJusBrException
from lib.json_utils import default_json_encoder
from lib.pje.service import get_trf3_service
from lib.webdriver.driver import new_driver


class TestTrf3(unittest.TestCase):
    def setUp(self):
        self.driver = new_driver()

    def tearDown(self):
        self.driver.quit()

    def test_trf3_get_data_from_cpf_that_does_not_exists(self):
        with self.assertRaises(LibJusBrException) as context:
            get_trf3_service(self.driver).get_process_list(
                term='02382814349',

                grade='pje1g',
            )

        self.assertEqual('Sua pesquisa não encontrou nenhum processo disponível.', context.exception.message)

    def test_trf3_get_simple_data_for_cpf_06013333815(self):
        process_list = get_trf3_service(self.driver).get_process_list(
            term='06013333815',
            grade='pje1g',
        )

        print(json.dumps(list(map(dataclasses.asdict, process_list)), indent=2, default=default_json_encoder))

        self.assertEqual(4, len(process_list))

    def test_trf3_get_detailed_data_for_cpf_06013333815(self):
        detailed_data = get_trf3_service(self.driver).get_detailed_process(
            term='06013333815',
            grade='pje1g',
        )

        print(json.dumps(dataclasses.asdict(detailed_data), indent=2, default=default_json_encoder))

    def test_all(self):
        service = get_trf3_service(self.driver)

        service.get_detailed_processes(term='97613231887', grade='pje1g')
