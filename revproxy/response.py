from .utils import cookie_from_string

from django.http import HttpResponse

HOP_BY_HOP_HEADERS = (
    'connection', 'keep-alive', 'proxy-authenticate', 'proxy-authorization',
    'te', 'trailers', 'transfer-encoding', 'upgrade')


class HttpProxyResponse(HttpResponse):

    def __init__(self, proxy_response, *args, **kwargs):
        content = proxy_response.data or b''
        headers = proxy_response.headers
        status = proxy_response.status

        content_type = headers.get('Content-Type')
        super(HttpProxyResponse, self).__init__(content, status=status,
                                                content_type=content_type,
                                                *args, **kwargs)

        for header, value in headers.items():
            if header.lower() not in HOP_BY_HOP_HEADERS:
                if header.lower() not in 'set-cookie':
                    self[header.title()] = value

        orig_response = proxy_response._original_response
        cookies = orig_response.msg.getheaders('set-cookie')
        for cookie_string in cookies:
            # Ideal if pullrequest is accept:
            # set_cookie_header = proxy_response.headers.getlist('set-cookie')
            # for cookie_string in set_cookie_header:
            cookie_dict = cookie_from_string(cookie_string)
            if cookie_dict:  # if cookie is invalid cookie_dict will be None
                self.set_cookie(**cookie_dict)
