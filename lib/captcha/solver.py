from twocaptcha import TwoCaptcha

from lib.captcha.constants import TWO_CAPTCHA_KEY
from lib.exceptions import LibJusBrException
from lib.log_utils import get_logger

if not TWO_CAPTCHA_KEY:
    raise LibJusBrException('É necessário configurar a chave de API do captcha')
solver = TwoCaptcha(TWO_CAPTCHA_KEY)

log = get_logger(__name__)


def solve_image_captcha(img_b64_string):
    log.info('Solving image captcha')
    result = solver.normal(file=img_b64_string.split(',')[-1])
    code = result.get('code')
    log.info(f'Solved Image: {img_b64_string}')
    log.info(f'Captcha Result: {code}')
    return code


def solve_cloudflare_captcha(sitekey, url):
    log.info('Solving cloudflare captcha')
    result = solver.turnstile(sitekey=sitekey, url=url)
    code = result.get('code')
    log.info('Solved cloudflare captcha')
    log.info(f'Captcha Result: {code}')
    return code
