import logging

from .utils import cookie_from_string, should_stream

from django.http import HttpResponse, StreamingHttpResponse

HOP_BY_HOP_HEADERS = (
    'connection', 'keep-alive', 'proxy-authenticate', 'proxy-authorization',
    'te', 'trailers', 'transfer-encoding', 'upgrade')

IGNORE_HEADERS = HOP_BY_HOP_HEADERS + ('set-cookie', )

DEFAULT_AMT = 2 ** 16  # 65536 bytes

logger = logging.getLogger('revproxy.response')


def get_django_response(proxy_response):
    status = proxy_response.status
    headers = proxy_response.headers

    logger.debug('Proxy response headers: %s', headers)

    content_type = headers.get('Content-Type')

    logger.debug('Content-Type: %s', content_type)

    if should_stream(proxy_response):
        logger.info('Content-Length is bigger than %s', DEFAULT_AMT)
        response = StreamingHttpResponse(proxy_response.stream(DEFAULT_AMT),
                                         status=status,
                                         content_type=content_type)
    else:
        content = proxy_response.data or b''
        response = HttpResponse(content, status=status,
                                content_type=content_type)

    logger.info("Normalizing headers that aren't in IGNORE_HEADERS")
    for header, value in headers.items():
        if header.lower() not in IGNORE_HEADERS:
            response[header.title()] = value

    logger.debug('Response headers: %s', getattr(response, '_headers'))

    cookies = proxy_response.headers.getlist('set-cookie')
    logger.info('Checking for invalid cookies')
    for cookie_string in cookies:
        cookie_dict = cookie_from_string(cookie_string)
        # if cookie is invalid cookie_dict will be None
        if cookie_dict:
            response.set_cookie(**cookie_dict)

    logger.debug('Response cookies: %s', response.cookies)

    return response
