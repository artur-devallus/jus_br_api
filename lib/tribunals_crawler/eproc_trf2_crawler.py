from lib.captcha.solver import solve_cloudflare_captcha
from lib.tribunals_crawler.base_eproc_crawler import BaseEprocCrawler


class EprocTrf2Crawler(BaseEprocCrawler):
    BASE_URL = 'https://eproc-consulta.trf2.jus.br'
    QUERY_URL = '/eproc/externo_controlador.php?acao=processo_consulta_publica'

    def _solve_captcha(self, url, body, soup):
        site_key = soup.find('div', id='divInfraCaptcha').find('div')['data-sitekey']
        path_split = url.path.split('/')
        full_url = url.scheme + '://' + url.host + '/'.join(
            path_split[0:len(path_split) - 1] +
            ['controlador_ajax.php?acao_ajax=verifica_estado_captcha']
        )
        token = solve_cloudflare_captcha(
            site_key,
            full_url,
            useragent=self.http.session.headers['User-Agent']
        )
        body.append(('cf-turnstile-response', token))
        return body


if __name__ == '__main__':
    with EprocTrf2Crawler() as crl:
        print(crl.query_process_list(
            term='00128658770'
        ))
