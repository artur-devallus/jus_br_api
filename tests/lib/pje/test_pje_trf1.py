import dataclasses
import datetime
import json
import unittest

from lib.exceptions import LibJusBrException
from lib.json_utils import default_json_encoder
from lib.pje.service import get_trf1_service
from lib.webdriver.driver import new_driver


class TestTrf1(unittest.TestCase):
    def setUp(self):
        self.driver = new_driver()

    def tearDown(self):
        self.driver.quit()

    def test_trf1_get_data_from_cpf_that_does_not_exists(self):
        with self.assertRaises(LibJusBrException) as context:
            get_trf1_service(self.driver).get_process_list(
                term='02382814349',

                grade='pje1g',
            )

        self.assertEqual('Sua pesquisa não encontrou nenhum processo disponível.', context.exception.message)

    def test_trf1_get_simple_data_for_cpf_37626361334(self):
        process_list = get_trf1_service(self.driver).get_process_list(
            term='37626361334',
            grade='pje1g',
        )

        print(json.dumps(list(map(dataclasses.asdict, process_list)), indent=2, default=default_json_encoder))

        self.assertEqual(1, len(process_list))
        simple_data = process_list[0]

        self.assertIsNotNone(simple_data)
        self.assertEqual('PROCEDIMENTO DO JUIZADO ESPECIAL CÍVEL', simple_data.process_class)
        self.assertEqual('PJEC', simple_data.process_class_abv)
        self.assertEqual('1055123-21.2021.4.01.3700', simple_data.process_number)
        self.assertEqual('Aposentadoria Rural (Art. 48/51)', simple_data.subject)
        self.assertEqual('RAIMUNDO NONATO CAMPELO', simple_data.plaintiff)
        self.assertEqual('INSTITUTO NACIONAL DO SEGURO SOCIAL', simple_data.defendant)
        self.assertEqual('Arquivado Definitivamente', simple_data.status)
        self.assertEqual(datetime.datetime(2025, 10, 7, 15, 28, 31), simple_data.last_update)

    def test_trf1_get_detailed_data_for_cpf_37626361334(self):
        service = get_trf1_service(self.driver)
        process_list = service.get_process_list(term='09058370372', grade='pje1g')
        for p in process_list[1:]:
            service.get_detailed_process(term='09058370372', grade='pje1g', process_index_or_number=p.process_number)

        detailed_data = get_trf1_service(self.driver).get_detailed_process(
            term='09058370372',
            grade='pje1g',
        )

        print(json.dumps(dataclasses.asdict(detailed_data), indent=2, default=default_json_encoder))

        self.assertIsNotNone(detailed_data)
        self.assertIsNotNone(detailed_data.process)
        self.assertEqual('1055123-21.2021.4.01.3700', detailed_data.process.process_number)
        self.assertEqual(datetime.date(2021, 12, 3), detailed_data.process.distribution_date)
        self.assertEqual('Seção Judiciária do Maranhão', detailed_data.process.jurisdiction)
        self.assertEqual('PROCEDIMENTO DO JUIZADO ESPECIAL CÍVEL (436)', detailed_data.process.judicial_class)
        self.assertEqual('7ª Vara Federal de Juizado Especial Cível da SJMA', detailed_data.process.judge_entity)
        self.assertEqual(
            'DIREITO PREVIDENCIÁRIO (195) - '
            'Benefícios em Espécie (6094) - '
            'Aposentadoria por Idade (Art. 48/51) (6096) - '
            'Aposentadoria Rural (Art. 48/51) (6098',
            detailed_data.process.subject
        )
        self.assertIsNotNone(detailed_data.case_parties)
        self.assertIsNotNone(detailed_data.case_parties.active)
        self.assertIsNotNone(detailed_data.case_parties.passive)
        self.assertEqual(2, len(detailed_data.case_parties.active))
        self.assertEqual(1, len(detailed_data.case_parties.passive))

        self.assertEqual('RAIMUNDO NONATO CAMPELO', detailed_data.case_parties.active[0].name)
        self.assertEqual('AUTOR', detailed_data.case_parties.active[0].role)
        self.assertIsNotNone(detailed_data.case_parties.active[0].documents)
        self.assertEqual(1, len(detailed_data.case_parties.active[0].documents))
        self.assertEqual('cpf', detailed_data.case_parties.active[0].attachments[0].type)
        self.assertEqual('37626361334', detailed_data.case_parties.active[0].attachments[0].value)

        self.assertEqual('ANA MARIA MENEZES RODRIGUES', detailed_data.case_parties.active[1].name)
        self.assertEqual('ADVOGADO', detailed_data.case_parties.active[1].role)
        self.assertIsNotNone(detailed_data.case_parties.active[1].documents)
        self.assertEqual(2, len(detailed_data.case_parties.active[1].documents))
        self.assertEqual('oab', detailed_data.case_parties.active[1].attachments[0].type)
        self.assertEqual('MA10539', detailed_data.case_parties.active[1].attachments[0].value)
        self.assertEqual('cpf', detailed_data.case_parties.active[1].documents[1].type)
        self.assertEqual('80153020300', detailed_data.case_parties.active[1].documents[1].value)

        self.assertEqual('INSTITUTO NACIONAL DO SEGURO SOCIAL', detailed_data.case_parties.passive[0].name)
        self.assertEqual('REU', detailed_data.case_parties.passive[0].role)
        self.assertIsNotNone(detailed_data.case_parties.passive[0].documents)
        self.assertEqual(1, len(detailed_data.case_parties.passive[0].documents))
        self.assertEqual('cnpj', detailed_data.case_parties.passive[0].attachments[0].type)
        self.assertEqual('29979036000221', detailed_data.case_parties.passive[0].attachments[0].value)

        self.assertIsNotNone(detailed_data.movements)
        self.assertEqual(39, len(detailed_data.movements))

        self.assertEqual('Arquivado Definitivamente', detailed_data.movements[0].description)
        self.assertEqual(datetime.datetime(2025, 10, 7, 15, 28, 31), detailed_data.movements[0].created_at)
        self.assertIsNone(detailed_data.movements[0].attachments[0].document_ref)
        self.assertIsNone(detailed_data.movements[0].attachments[0].document_date)

        self.assertEqual('Decorrido prazo de INSTITUTO NACIONAL DO SEGURO SOCIAL em 06/10/2025 23:59.',
                         detailed_data.movements[1].description)
        self.assertEqual(datetime.datetime(2025, 10, 7, 1, 17, 52), detailed_data.movements[1].created_at)
        self.assertIsNone(detailed_data.movements[1].attachments[0].document_ref)
        self.assertIsNone(detailed_data.movements[1].attachments[0].document_date)

        self.assertEqual('Juntada de manifestação', detailed_data.movements[2].description)
        self.assertEqual(datetime.datetime(2025, 10, 1, 18, 6, 6), detailed_data.movements[2].created_at)
        self.assertIsNone(detailed_data.movements[2].attachments[0].document_ref)
        self.assertIsNone(detailed_data.movements[2].attachments[0].document_date)

        self.assertEqual('Publicado Sentença Tipo C em 18/09/2025.', detailed_data.movements[3].description)
        self.assertEqual(datetime.datetime(2025, 9, 18, 0, 51, 12), detailed_data.movements[3].created_at)
        self.assertEqual('Sentença Tipo C (Sentença Tipo C)', detailed_data.movements[3].attachments[0].document_ref)
        self.assertEqual(datetime.datetime(2025, 7, 30, 16, 45, 20),
                         detailed_data.movements[3].attachments[0].document_date)

        self.assertEqual('Disponibilizado no DJ Eletrônico em 17/09/2025', detailed_data.movements[4].description)
        self.assertEqual(datetime.datetime(2025, 9, 18, 0, 51, 8), detailed_data.movements[4].created_at)
        self.assertEqual('Sentença Tipo C (Sentença Tipo C)', detailed_data.movements[4].attachments[0].document_ref)
        self.assertEqual(datetime.datetime(2025, 7, 30, 16, 45, 20),
                         detailed_data.movements[4].attachments[0].document_date)

        self.assertEqual('Processo devolvido à Secretaria', detailed_data.movements[5].description)
        self.assertEqual(datetime.datetime(2025, 9, 16, 15, 56, 59), detailed_data.movements[5].created_at)
        self.assertIsNone(detailed_data.movements[5].attachments[0].document_ref)
        self.assertIsNone(detailed_data.movements[5].attachments[0].document_date)

        self.assertEqual('Juntada de Certidão', detailed_data.movements[6].description)
        self.assertEqual(datetime.datetime(2025, 9, 16, 15, 56, 58), detailed_data.movements[6].created_at)
        self.assertIsNone(detailed_data.movements[6].attachments[0].document_ref)
        self.assertIsNone(detailed_data.movements[6].attachments[0].document_date)

        self.assertEqual('Expedida/certificada a comunicação eletrônica', detailed_data.movements[7].description)
        self.assertEqual(datetime.datetime(2025, 9, 16, 15, 56, 58), detailed_data.movements[7].created_at)
        self.assertEqual('Sentença Tipo C (Sentença Tipo C)', detailed_data.movements[7].attachments[0].document_ref)
        self.assertEqual(datetime.datetime(2025, 7, 30, 16, 45, 20),
                         detailed_data.movements[7].attachments[0].document_date)

        self.assertEqual('Expedição de Publicação ao Diário de Justiça Eletrônico Nacional.',
                         detailed_data.movements[8].description)
        self.assertEqual(datetime.datetime(2025, 9, 16, 15, 56, 57), detailed_data.movements[8].created_at)
        self.assertIsNone(detailed_data.movements[8].attachments[0].document_ref)
        self.assertIsNone(detailed_data.movements[8].attachments[0].document_date)

        self.assertEqual('Expedição de Publicação ao Diário de Justiça Eletrônico Nacional.',
                         detailed_data.movements[9].description)
        self.assertEqual(datetime.datetime(2025, 9, 16, 15, 56, 57), detailed_data.movements[9].created_at)
        self.assertEqual('Sentença Tipo C (Sentença Tipo C)', detailed_data.movements[9].attachments[0].document_ref)
        self.assertEqual(datetime.datetime(2025, 7, 30, 16, 45, 20),
                         detailed_data.movements[9].attachments[0].document_date)

        self.assertEqual('Extinto o processo por ausência das condições da ação',
                         detailed_data.movements[10].description)
        self.assertEqual(datetime.datetime(2025, 9, 16, 15, 56, 56), detailed_data.movements[10].created_at)
        self.assertEqual('Sentença Tipo C (Sentença Tipo C)', detailed_data.movements[10].attachments[0].document_ref)
        self.assertEqual(datetime.datetime(2025, 7, 30, 16, 45, 20),
                         detailed_data.movements[10].attachments[0].document_date)

        self.assertEqual('Conclusos para julgamento', detailed_data.movements[11].description)
        self.assertEqual(datetime.datetime(2025, 1, 2, 0, 28, 10), detailed_data.movements[11].created_at)
        self.assertIsNone(detailed_data.movements[11].attachments[0].document_ref)
        self.assertIsNone(detailed_data.movements[11].attachments[0].document_date)

        self.assertEqual('Decorrido prazo de RAIMUNDO NONATO CAMPELO em 03/12/2024 23:59.',
                         detailed_data.movements[12].description)
        self.assertEqual(datetime.datetime(2024, 12, 4, 0, 27, 33), detailed_data.movements[12].created_at)
        self.assertIsNone(detailed_data.movements[12].attachments[0].document_ref)
        self.assertIsNone(detailed_data.movements[12].attachments[0].document_date)

        self.assertEqual('Juntada de Certidão', detailed_data.movements[13].description)
        self.assertEqual(datetime.datetime(2024, 11, 6, 0, 52, 26), detailed_data.movements[13].created_at)
        self.assertIsNone(detailed_data.movements[13].attachments[0].document_ref)
        self.assertIsNone(detailed_data.movements[13].attachments[0].document_date)

        self.assertEqual('Expedida/certificada a comunicação eletrônica', detailed_data.movements[14].description)
        self.assertEqual(datetime.datetime(2024, 11, 6, 0, 52, 26), detailed_data.movements[14].created_at)
        self.assertEqual('Ato ordinatório (Ato ordinatório)', detailed_data.movements[14].attachments[0].document_ref)
        self.assertEqual(datetime.datetime(2024, 11, 6, 0, 48, 45),
                         detailed_data.movements[14].attachments[0].document_date)

        self.assertEqual('Ato ordinatório praticado', detailed_data.movements[15].description)
        self.assertEqual(datetime.datetime(2024, 11, 6, 0, 52, 26), detailed_data.movements[15].created_at)
        self.assertEqual('Ato ordinatório (Ato ordinatório)', detailed_data.movements[15].attachments[0].document_ref)
        self.assertEqual(datetime.datetime(2024, 11, 6, 0, 48, 45),
                         detailed_data.movements[15].attachments[0].document_date)

        self.assertEqual('Juntada de dossiê - prevjud', detailed_data.movements[16].description)
        self.assertEqual(datetime.datetime(2024, 6, 28, 1, 9, 1), detailed_data.movements[16].created_at)
        self.assertIsNone(detailed_data.movements[16].attachments[0].document_ref)
        self.assertIsNone(detailed_data.movements[16].attachments[0].document_date)

        self.assertEqual('Juntada de dossiê - prevjud', detailed_data.movements[17].description)
        self.assertEqual(datetime.datetime(2024, 6, 28, 1, 9, 1), detailed_data.movements[17].created_at)
        self.assertIsNone(detailed_data.movements[17].attachments[0].document_ref)
        self.assertIsNone(detailed_data.movements[17].attachments[0].document_date)

        self.assertEqual('Juntada de dossiê - prevjud', detailed_data.movements[18].description)
        self.assertEqual(datetime.datetime(2024, 6, 28, 1, 9, 1), detailed_data.movements[18].created_at)
        self.assertIsNone(detailed_data.movements[18].attachments[0].document_ref)
        self.assertIsNone(detailed_data.movements[18].attachments[0].document_date)

        self.assertEqual('Juntada de dossiê - prevjud', detailed_data.movements[19].description)
        self.assertEqual(datetime.datetime(2024, 6, 28, 1, 9), detailed_data.movements[19].created_at)
        self.assertIsNone(detailed_data.movements[19].attachments[0].document_ref)
        self.assertIsNone(detailed_data.movements[19].attachments[0].document_date)

        self.assertEqual('Juntada de dossiê - prevjud', detailed_data.movements[20].description)
        self.assertEqual(datetime.datetime(2024, 6, 28, 1, 9), detailed_data.movements[20].created_at)
        self.assertIsNone(detailed_data.movements[20].attachments[0].document_ref)
        self.assertIsNone(detailed_data.movements[20].attachments[0].document_date)

        self.assertEqual('Juntada de Informação', detailed_data.movements[21].description)
        self.assertEqual(datetime.datetime(2024, 6, 20, 16, 3, 16), detailed_data.movements[21].created_at)
        self.assertIsNone(detailed_data.movements[21].attachments[0].document_ref)
        self.assertIsNone(detailed_data.movements[21].attachments[0].document_date)

        self.assertEqual('Juntada de Informação', detailed_data.movements[22].description)
        self.assertEqual(datetime.datetime(2024, 2, 22, 13, 51, 23), detailed_data.movements[22].created_at)
        self.assertIsNone(detailed_data.movements[22].attachments[0].document_ref)
        self.assertIsNone(detailed_data.movements[22].attachments[0].document_date)

        self.assertEqual('Juntada de Informação', detailed_data.movements[23].description)
        self.assertEqual(datetime.datetime(2023, 11, 13, 11, 42, 57), detailed_data.movements[23].created_at)
        self.assertIsNone(detailed_data.movements[23].attachments[0].document_ref)
        self.assertIsNone(detailed_data.movements[23].attachments[0].document_date)

        self.assertEqual('Juntada de Informação', detailed_data.movements[24].description)
        self.assertEqual(datetime.datetime(2023, 5, 10, 13, 19, 22), detailed_data.movements[24].created_at)
        self.assertIsNone(detailed_data.movements[24].attachments[0].document_ref)
        self.assertIsNone(detailed_data.movements[24].attachments[0].document_date)

        self.assertEqual('Decorrido prazo de RAIMUNDO NONATO CAMPELO em 06/03/2023 23:59.',
                         detailed_data.movements[25].description)
        self.assertEqual(datetime.datetime(2023, 3, 7, 2, 15), detailed_data.movements[25].created_at)
        self.assertIsNone(detailed_data.movements[25].attachments[0].document_ref)
        self.assertIsNone(detailed_data.movements[25].attachments[0].document_date)

        self.assertEqual('Expedida/certificada a comunicação eletrônica', detailed_data.movements[26].description)
        self.assertEqual(datetime.datetime(2023, 2, 15, 13, 21, 39), detailed_data.movements[26].created_at)
        self.assertIsNone(detailed_data.movements[26].attachments[0].document_ref)
        self.assertIsNone(detailed_data.movements[26].attachments[0].document_date)

        self.assertEqual('Expedição de Outros documentos.', detailed_data.movements[27].description)
        self.assertEqual(datetime.datetime(2023, 2, 15, 13, 21, 39), detailed_data.movements[27].created_at)
        self.assertIsNone(detailed_data.movements[27].attachments[0].document_ref)
        self.assertIsNone(detailed_data.movements[27].attachments[0].document_date)

        self.assertEqual('Juntada de Informação', detailed_data.movements[28].description)
        self.assertEqual(datetime.datetime(2023, 2, 14, 17, 39, 46), detailed_data.movements[28].created_at)
        self.assertIsNone(detailed_data.movements[28].attachments[0].document_ref)
        self.assertIsNone(detailed_data.movements[28].attachments[0].document_date)

        self.assertEqual('Juntada de contestação', detailed_data.movements[29].description)
        self.assertEqual(datetime.datetime(2022, 7, 25, 12, 51, 29), detailed_data.movements[29].created_at)
        self.assertIsNone(detailed_data.movements[29].attachments[0].document_ref)
        self.assertIsNone(detailed_data.movements[29].attachments[0].document_date)

        self.assertEqual('Expedida/certificada a citação eletrônica', detailed_data.movements[30].description)
        self.assertEqual(datetime.datetime(2022, 7, 21, 14, 34, 59), detailed_data.movements[30].created_at)
        self.assertIsNone(detailed_data.movements[30].attachments[0].document_ref)
        self.assertIsNone(detailed_data.movements[30].attachments[0].document_date)

        self.assertEqual('Expedição de Outros documentos.', detailed_data.movements[31].description)
        self.assertEqual(datetime.datetime(2022, 7, 21, 14, 34, 58), detailed_data.movements[31].created_at)
        self.assertIsNone(detailed_data.movements[31].attachments[0].document_ref)
        self.assertIsNone(detailed_data.movements[31].attachments[0].document_date)

        self.assertEqual('Processo devolvido à Secretaria', detailed_data.movements[32].description)
        self.assertEqual(datetime.datetime(2022, 7, 6, 18, 31, 47), detailed_data.movements[32].created_at)
        self.assertIsNone(detailed_data.movements[32].attachments[0].document_ref)
        self.assertIsNone(detailed_data.movements[32].attachments[0].document_date)

        self.assertEqual('Proferido despacho de mero expediente', detailed_data.movements[33].description)
        self.assertEqual(datetime.datetime(2022, 7, 6, 18, 31, 45), detailed_data.movements[33].created_at)
        self.assertEqual('Despacho (Despacho)', detailed_data.movements[33].attachments[0].document_ref)
        self.assertEqual(datetime.datetime(2022, 7, 4, 10, 2, 54),
                         detailed_data.movements[33].attachments[0].document_date)

        self.assertEqual('Conclusos para despacho', detailed_data.movements[34].description)
        self.assertEqual(datetime.datetime(2022, 6, 9, 16, 23, 9), detailed_data.movements[34].created_at)
        self.assertIsNone(detailed_data.movements[34].attachments[0].document_ref)
        self.assertIsNone(detailed_data.movements[34].attachments[0].document_date)

        self.assertEqual(
            'Remetidos os Autos (em diligência) da Distribuição ao 7ª Vara Federal de Juizado Especial Cível da SJMA',
            detailed_data.movements[35].description)
        self.assertEqual(datetime.datetime(2021, 12, 3, 23, 30, 49), detailed_data.movements[35].created_at)
        self.assertIsNone(detailed_data.movements[35].attachments[0].document_ref)
        self.assertIsNone(detailed_data.movements[35].attachments[0].document_date)

        self.assertEqual('Juntada de Informação de Prevenção', detailed_data.movements[36].description)
        self.assertEqual(datetime.datetime(2021, 12, 3, 23, 30, 48), detailed_data.movements[36].created_at)
        self.assertIsNone(detailed_data.movements[36].attachments[0].document_ref)
        self.assertIsNone(detailed_data.movements[36].attachments[0].document_date)

        self.assertEqual('Recebido pelo Distribuidor', detailed_data.movements[37].description)
        self.assertEqual(datetime.datetime(2021, 12, 3, 19, 5, 45), detailed_data.movements[37].created_at)
        self.assertIsNone(detailed_data.movements[37].attachments[0].document_ref)
        self.assertIsNone(detailed_data.movements[37].attachments[0].document_date)

        self.assertEqual('Distribuído por sorteio', detailed_data.movements[38].description)
        self.assertEqual(datetime.datetime(2021, 12, 3, 19, 5, 44), detailed_data.movements[38].created_at)
        self.assertIsNone(detailed_data.movements[38].attachments[0].document_ref)
        self.assertIsNone(detailed_data.movements[38].attachments[0].document_date)
