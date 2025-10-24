from lib.captcha.solver import solve_image_captcha
from lib.json_utils import json_dump
from lib.tribunals_crawler.base_eproc_crawler import BaseEprocCrawler


class _EprocTrf6Crawler(BaseEprocCrawler):
    QUERY_URL = '/eproc/externo_controlador.php?acao=processo_consulta_publica'

    def _solve_captcha(self, url, body, soup):
        body.pop()
        body.append((
            'txtInfraCaptcha', solve_image_captcha(soup.find('label', id='lblInfraCaptcha').find('img')['src'])
        ))
        return body


class Eproc1gTrf6Crawler(_EprocTrf6Crawler):
    BASE_URL = 'https://eproc1g.trf6.jus.br'


class Eproc2gTrf6Crawler(_EprocTrf6Crawler):
    BASE_URL = 'https://eproc2g.trf6.jus.br'


if __name__ == '__main__':
    with Eproc1gTrf6Crawler() as crl:
        json_dump(crl.detail_process_list(
            term='34775889753'
        ))
