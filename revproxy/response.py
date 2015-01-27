from .utils import cookie_from_string, should_stream

from django.http import HttpResponse, StreamingHttpResponse

HOP_BY_HOP_HEADERS = (
    'connection', 'keep-alive', 'proxy-authenticate', 'proxy-authorization',
    'te', 'trailers', 'transfer-encoding', 'upgrade')

IGNORE_HEADERS = HOP_BY_HOP_HEADERS + ('set-cookie', )

DEFAULT_AMT = 2 ** 16


def get_django_response(proxy_response):
    status = proxy_response.status
    headers = proxy_response.headers

    content_type = headers.get('Content-Type')

    if should_stream(proxy_response):
        response = StreamingHttpResponse(proxy_response.stream(DEFAULT_AMT),
                                         status=status,
                                         content_type=content_type)
    else:
        content = proxy_response.data or b''
        response = HttpResponse(content, status=status,
                                content_type=content_type)

    for header, value in headers.items():
        if header.lower() not in IGNORE_HEADERS:
            response[header.title()] = value

    orig_response = proxy_response._original_response
    if orig_response:
        # Ideally we should use:

        # orig_headers = proxy_response.headers
        # set_cookie_header = orig_headers.getlist('set-cookie')
        # for cookie_string in set_cookie_header:

        # the code above depends on that PR:
        #   https://github.com/shazow/urllib3/pull/534

        cookies = orig_response.msg.getheaders('set-cookie')
        for cookie_string in cookies:
            cookie_dict = cookie_from_string(cookie_string)
            # if cookie is invalid cookie_dict will be None
            if cookie_dict:
                response.set_cookie(**cookie_dict)

    return response
