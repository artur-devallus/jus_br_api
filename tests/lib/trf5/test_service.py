import unittest

from lib.exceptions import LibJusBrException
from lib.trf5.service import get_trf5_service
from lib.webdriver.driver import new_driver


class TestTrf5(unittest.TestCase):
    def setUp(self):
        self.driver = new_driver()

    def tearDown(self):
        self.driver.quit()

    def test_trf5_get_data_from_cpf_that_does_not_exists(self):
        with self.assertRaises(LibJusBrException) as context:
            get_trf5_service(self.driver).get_process_list(
                term='02382814349',
            )

        self.assertEqual('Foram encontrados: 0 resultados', context.exception.message)

    def test_trf1_get_simple_data_for_cpf_46191488300(self):
        process_list = get_trf5_service(self.driver).get_process_list(
            term='46191488300',
        )

        self.assertEqual(1, len(process_list))
        self.assertEqual('APELAÇÃO / REMESSA NECESSÁRIA', process_list[0].process_class)
        self.assertEqual('0806425-90.2014.4.05.8100', process_list[0].process_number)
        self.assertEqual('MARIA DAS GRACAS FONSECA DO CARMO e outro', process_list[0].plaintiff)
        self.assertEqual('INSTITUTO NACIONAL DO SEGURO SOCIAL - INSS e outro', process_list[0].defendant)
        self.assertEqual(
            'DIREITO PREVIDENCIÁRIO|RMI - Renda Mensal Inicial, Reajustes e Revisões Específicas|Reajustes e Revisões Específicos|Abono da Lei 8.178/91|',
            process_list[0].subject)
        self.assertEqual('Baixa Definitiva', process_list[0].status)

    def test_trf1_get_detailed_data_for_cpf_46191488300(self):
        detail_process = get_trf5_service(self.driver).get_detailed_process(
            term='46191488300',
        )
        self.assertIsNotNone(detail_process)
        self.assertEqual(182, len(detail_process.movements))
