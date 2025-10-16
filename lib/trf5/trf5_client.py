import base64
import time

from lib.captcha.solver import solve_image_captcha
from lib.format_utils import format_cpf
from lib.http_client import HttpClient


class PjeTrf5Crawler:
    BASE_URL = "https://pje.trf5.jus.br"

    def __init__(self):
        self._http = HttpClient(self.BASE_URL)

    def get_captcha(self) -> str:
        """Baixa captcha e retorna como base64."""
        # Gera sessão
        self._http.get("/pje/ConsultaPublica/listView.seam")

        # Captcha com parâmetro f dinâmico
        f_param = int(time.time() * 1000)
        jsession = self._http.session.cookies.get("JSESSIONID")
        captcha_url = f"/pjeconsulta/seam/resource/captcha;jsessionid={jsession}?f={f_param}"

        r = self._http.get(captcha_url)
        return base64.encodebytes(r.content).decode("utf-8")

    def _post_form(self, data: dict) -> str:
        """Envia POST para a página de consulta mantendo cookies e headers."""
        jsession = self._http.session.cookies.get("JSESSIONID")
        url = f"/pjeconsulta/ConsultaPublica/listView.seam;jsessionid={jsession}"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": self.BASE_URL,
            "Referer": f"{self.BASE_URL}/pje/ConsultaPublica/listView.seam",
        }
        response = self._http.post(url, data=data, headers=headers)
        return response.text

    def query(self, cpf: str) -> str:
        captcha = solve_image_captcha(self.get_captcha(), numeric=1)

        # POST inicial para manter sessão (todos campos vazios)
        initial_data = {
            "AJAXREQUEST": "_viewRoot",
            "consultaPublicaForm:Processo:jurisdicaoSecaoDecoration:jurisdicaoSecao": "org.jboss.seam.ui.NoSelectionConverter.noSelectionValue",
            "consultaPublicaForm:Processo:ProcessoDecoration:Processo": "_______-__.____._.__.____",
            "consultaPublicaForm:Processo:j_id119:numeroProcessoPesqsuisaOriginario": "",
            "consultaPublicaForm:nomeParte:nomeParteDecoration:nomeParte": "",
            "consultaPublicaForm:nomeParteAdvogado:nomeParteAdvogadoDecoration:nomeParteAdvogadoDecoration:nomeParteAdvogado": "",
            "consultaPublicaForm:classeJudicial:idDecorateclasseJudicial:classeJudicial": "",
            "consultaPublicaForm:classeJudicial:idDecorateclasseJudicial:j_id207_selection": "",
            "consultaPublicaForm:numeroCPFCNPJ:numeroCPFCNPJRadioCPFCNPJ:numeroCPFCNPJCNPJ": "",
            "consultaPublicaForm:numeroOABParte:numeroOABParteDecoration:numeroOABParteEstadoCombo": "org.jboss.seam.ui.NoSelectionConverter.noSelectionValue",
            "consultaPublicaForm:numeroOABParte:numeroOABParteDecoration:numeroOABParte": "",
            "consultaPublicaForm:numeroOABParte:numeroOABParteDecoration:j_id258": "",
            "consultaPublicaForm:captcha:j_id268:verifyCaptcha": "",
            "consultaPublicaForm": "consultaPublicaForm",
            "autoScroll": "",
            "javax.faces.ViewState": "j_id1",
            "consultaPublicaForm:numeroCPFCNPJ:numeroCPFCNPJRadioCPFCNPJ:j_id229": "on",
            "consultaPublicaForm:numeroCPFCNPJ:numeroCPFCNPJRadioCPFCNPJ:j_id230": "consultaPublicaForm:numeroCPFCNPJ:numeroCPFCNPJRadioCPFCNPJ:j_id230",
            "ajaxSingle": "consultaPublicaForm:numeroCPFCNPJ:numeroCPFCNPJRadioCPFCNPJ:j_id229",
            "AJAX:EVENTS_COUNT": "1"
        }
        self._post_form(initial_data)

        # POST de consulta real com CPF e captcha
        query_data = {
            "AJAXREQUEST": "_viewRoot",
            "consultaPublicaForm:Processo:jurisdicaoSecaoDecoration:jurisdicaoSecao": "org.jboss.seam.ui.NoSelectionConverter.noSelectionValue",
            "consultaPublicaForm:Processo:ProcessoDecoration:Processo": "_______-__.____._.__.____",
            "consultaPublicaForm:Processo:j_id119:numeroProcessoPesqsuisaOriginario": "",
            "consultaPublicaForm:nomeParte:nomeParteDecoration:nomeParte": "",
            "consultaPublicaForm:nomeParteAdvogado:nomeParteAdvogadoDecoration:nomeParteAdvogadoDecoration:nomeParteAdvogado": "",
            "consultaPublicaForm:classeJudicial:idDecorateclasseJudicial:classeJudicial": "",
            "consultaPublicaForm:classeJudicial:idDecorateclasseJudicial:j_id207_selection": "",
            "consultaPublicaForm:numeroCPFCNPJ:numeroCPFCNPJRadioCPFCNPJ:j_id229": "on",
            "consultaPublicaForm:numeroCPFCNPJ:numeroCPFCNPJRadioCPFCNPJ:numeroCPFCNPJCPF": format_cpf(cpf),
            "consultaPublicaForm:numeroOABParte:numeroOABParteDecoration:numeroOABParteEstadoCombo": "org.jboss.seam.ui.NoSelectionConverter.noSelectionValue",
            "consultaPublicaForm:numeroOABParte:numeroOABParteDecoration:numeroOABParte": "",
            "consultaPublicaForm:numeroOABParte:numeroOABParteDecoration:j_id258": "",
            "consultaPublicaForm:captcha:j_id268:verifyCaptcha": captcha,
            "consultaPublicaForm": "consultaPublicaForm",
            "autoScroll": "",
            "javax.faces.ViewState": "j_id1",
            "consultaPublicaForm:pesq": "consultaPublicaForm:pesq",
            "AJAX:EVENTS_COUNT": "1"
        }

        return self._post_form(query_data)

    def close(self):
        self._http.close()


if __name__ == "__main__":
    crawler = PjeTrf5Crawler()
    try:
        html_result = crawler.query("31768806349")
        print("HTML retornado:")
        print(html_result)
    finally:
        crawler.close()
