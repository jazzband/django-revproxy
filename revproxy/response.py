from .utils import cookie_from_string

from django.http import HttpResponse

HOP_BY_HOP_HEADERS = (
    'connection', 'keep-alive', 'proxy-authenticate', 'proxy-authorization',
    'te', 'trailers', 'transfer-encoding', 'upgrade')

IGNORE_HEADERS = HOP_BY_HOP_HEADERS + ('set-cookie', )


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
            if header.lower() not in IGNORE_HEADERS:
                self[header.title()] = value

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
                    self.set_cookie(**cookie_dict)
