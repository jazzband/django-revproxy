
import urllib2


class NoHTTPRedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_301(self, *args, **kwargs):
        return None

    http_error_302 = http_error_303 = http_error_307 = http_error_301


IGNORE_HEADERS = (
    'HTTP_ACCEPT_ENCODING', # We want content to be uncompressed so
                            #   we remove the Accept-Encoding from
                            #   original request
)

def normalize_headers(request):
    norm_headers = {}
    for header, value in request.META.items():
        if header == 'HTTP_HOST':
            continue

        if header.startswith('HTTP_') and header not in IGNORE_HEADERS:
            norm_header = header[5:].title().replace('_', '-')
            norm_headers[norm_header] = value

    return norm_headers
