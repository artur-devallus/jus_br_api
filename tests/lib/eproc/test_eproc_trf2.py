import dataclasses
import json
import unittest

from lib.eproc.service import get_trf2_service
from lib.exceptions import LibJusBrException
from lib.json_utils import default_json_encoder
from lib.webdriver.driver import new_driver


class TestTrf6(unittest.TestCase):
    def setUp(self):
        self.driver = new_driver()

    def tearDown(self):
        self.driver.quit()

    def test_trf2_get_data_from_cpf_that_does_not_exists(self):
        with self.assertRaises(LibJusBrException) as context:
            get_trf2_service(self.driver).get_process_list(
                term='02382814349',
                grade='eproc1g',
            )

        self.assertEqual('Nenhum registro encontrado.', context.exception.message)

    def test_trf2_get_simple_data_for_cpf_00128658770(self):
        process_list = get_trf2_service(self.driver).get_process_list(
            term='00128658770',
            grade='eproc1g',
        )

        print(json.dumps(list(map(dataclasses.asdict, process_list)), indent=2, default=default_json_encoder))

        self.assertEqual(4, len(process_list))

        self.assertEqual('0005636-72.1993.4.01.3800', process_list[0].process_number)
        self.assertEqual('NOEMIA GUERREIRO ABREU', process_list[0].plaintiff)
        self.assertEqual('INSTITUTO NACIONAL DO SEGURO SOCIAL', process_list[0].defendant)
        self.assertEqual('Assunto não disponível', process_list[0].subject)
        self.assertIsNone(process_list[0].process_class)
        self.assertIsNone(process_list[0].process_class_abv)
        self.assertIsNone(process_list[0].status)

    def test_trf2_get_detailed_data_for_cpf_00128658770(self):
        detailed_data = get_trf2_service(self.driver).get_detailed_process(
            term='00128658770',
            grade='eproc1g',
        )

        print(json.dumps(dataclasses.asdict(detailed_data), indent=2, default=default_json_encoder))
        self.assertIsNotNone(detailed_data)
