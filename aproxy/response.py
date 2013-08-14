
from django.http import HttpResponse


HOP_BY_HOP_HEADERS = (
    'connection', 'keep-alive', 'proxy-authenticate', 'proxy-authorization',
    'te', 'trailers', 'transfer-encoding', 'upgrade')


class HttpProxyResponse(HttpResponse):

    def __init__(self, proxy_response, *args, **kwargs):
        body = proxy_response.read()
        headers = proxy_response.headers
        status = proxy_response.getcode()

        super(HttpProxyResponse, self).__init__(body, status=status,
                                                *args, **kwargs)

        for header, value in headers.items():
            if header.lower() not in HOP_BY_HOP_HEADERS:
                self[header.title()] = value
