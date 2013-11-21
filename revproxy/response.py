
from django.http import HttpResponse


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
        if self._charset:
            self.unicode_content = content.decode(self._charset)
        else:
            self.unicode_content = None

        for header, value in headers.items():
            if header.lower() not in HOP_BY_HOP_HEADERS:
                self[header.title()] = value
