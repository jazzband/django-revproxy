from .utils import cookie_from_string, should_stream

from django.http import HttpResponse, StreamingHttpResponse

#: Headers used only for HOP-BY-HOP transport
HOP_BY_HOP_HEADERS = (
    'connection', 'keep-alive', 'proxy-authenticate', 'proxy-authorization',
    'te', 'trailers', 'transfer-encoding', 'upgrade')

#: Headers that must be ignored
IGNORE_HEADERS = HOP_BY_HOP_HEADERS + ('set-cookie', )

#: Default number of bytes that are going to be read in a file lecture
DEFAULT_AMT = 2 ** 16


def get_django_response(proxy_response):
    """This method is used to create an appropriate response based on the
    Content-Length of the proxy_response. If the content is bigger than
    MIN_STREAMING_LENGTH, which is found on utils.py,
    than django.http.StreamingHttpResponse will be created,
    else a django.http.HTTPResponse will be created instead

    :param proxy_response: An Instance of urllib3.response.HTTPResponse that
                           will create an appropriate response
    :returns: Returns an appropriate response based on the proxy_response
              content-length
    """
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

    cookies = proxy_response.headers.getlist('set-cookie')
    for cookie_string in cookies:
        cookie_dict = cookie_from_string(cookie_string)
        # if cookie is invalid cookie_dict will be None
        if cookie_dict:
            response.set_cookie(**cookie_dict)

    return response
