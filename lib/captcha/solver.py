from twocaptcha import TwoCaptcha

from lib.captcha.constants import TWO_CAPTCHA_KEY
from lib.exceptions import LibJusBrException
from lib.log_utils import get_logger

if not TWO_CAPTCHA_KEY:
    raise LibJusBrException('É necessário configurar a chave de API do captcha')
solver = TwoCaptcha(TWO_CAPTCHA_KEY)

log = get_logger(__name__)


def solve_image_captcha(img_b64_string, numeric=0):
    result = solver.normal(file=img_b64_string.split(',')[-1], numeric=numeric)
    code = result.get('code')
    return code


def solve_cloudflare_captcha(sitekey, url, **kwargs):
    result = solver.turnstile(sitekey=sitekey, url=url, **kwargs)
    code = result.get('code')
    return code
