from django.http import HttpResponse

from .utils import get_charset

HOP_BY_HOP_HEADERS = (
    'connection', 'keep-alive', 'proxy-authenticate', 'proxy-authorization',
    'te', 'trailers', 'transfer-encoding', 'upgrade')


class HttpProxyResponse(HttpResponse):

    def __init__(self, proxy_response, *args, **kwargs):
        content = proxy_response.read()
        headers = proxy_response.headers
        status = proxy_response.getcode()

        super(HttpProxyResponse, self).__init__(content, status=status,
                                                *args, **kwargs)

        content_type = headers.get('content-type', '')
        self._charset = get_charset(content_type)
        self.unicode_content = content.decode(self._charset)

        for header, value in headers.items():
            if header.lower() not in HOP_BY_HOP_HEADERS:
                self[header.title()] = value
