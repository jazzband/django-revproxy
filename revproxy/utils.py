
import re
import sys

if sys.version_info >= (3, 0, 0):  # pragma: no cover
    from urllib.request import HTTPRedirectHandler
else:  # pragma: no cover
    # Fallback to Python 2.7
    from urllib2 import HTTPRedirectHandler


IGNORE_HEADERS = (
    'HTTP_ACCEPT_ENCODING',  # We want content to be uncompressed so
                             #   we remove the Accept-Encoding from
                             #   original request
    'HTTP_HOST',
)


# Default from HTTP RFC 2616
#   See: http://www.w3.org/Protocols/rfc2616/rfc2616-sec3.html#sec3.7.1
DEFAULT_CHARSET = 'latin-1'


_get_charset_re = re.compile(r';\s*charset=(?P<charset>[^\s;]+)', re.I)


class NoHTTPRedirectHandler(HTTPRedirectHandler, object):
    def redirect_request(self, *args, **kwargs):
        return None


def get_charset(content_type):
    matched = _get_charset_re.search(content_type)
    if matched:
        # Extract the charset and strip its double quotes
        return matched.group('charset').replace('"', '')
    return DEFAULT_CHARSET


def required_header(header):
    if header in IGNORE_HEADERS:
        return False

    if header.startswith('HTTP_') or header == 'CONTENT_TYPE':
        return True

    return False


def normalize_headers(request):
    norm_headers = {}
    for header, value in request.META.items():
        if required_header(header):
            norm_header = header.replace('HTTP_', '').title().replace('_', '-')
            norm_headers[norm_header] = value

    return norm_headers


def encode_items(items):
    encoded = []
    for key, values in items:
        for value in values:
            encoded.append((key.encode('utf-8'), value.encode('utf-8')))
    return encoded
