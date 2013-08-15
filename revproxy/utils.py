
import urllib2


class NoHTTPRedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_301(self, *args, **kwargs):
        return None

    http_error_302 = http_error_303 = http_error_307 = http_error_301


def normalize_headers(request):
    norm_headers = {}
    for header, value in request.META.items():
        if header.startswith('HTTP_'):
            norm_header = header[5:].title().replace('_', '-')
            norm_headers[norm_header] = value

    return norm_headers
