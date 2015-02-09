
import re

import logging


IGNORE_HEADERS = (
    'HTTP_ACCEPT_ENCODING',  # We want content to be uncompressed so
                             #   we remove the Accept-Encoding from
                             #   original request
    'HTTP_HOST',
)


# Default from HTTP RFC 2616
#   See: http://www.w3.org/Protocols/rfc2616/rfc2616-sec3.html#sec3.7.1
DEFAULT_CHARSET = 'latin-1'

HTML_CONTENT_TYPES = (
    'text/html',
    'application/xhtml+xml'
)

MIN_STREAMING_LENGTH = 4 * 1024  # 4KB


_get_charset_re = re.compile(r';\s*charset=(?P<charset>[^\s;]+)', re.I)


def is_html_content_type(content_type):
    for html_content_type in HTML_CONTENT_TYPES:
        if content_type.startswith(html_content_type):
            return True

    return False


def should_stream(proxy_response):
    content_type = proxy_response.headers.get('Content-Type')

    if is_html_content_type(content_type):
        return False

    try:
        content_length = int(proxy_response.headers.get('Content-Length', 0))
    except ValueError:
        content_length = 0

    if not content_length or content_length > MIN_STREAMING_LENGTH:
        return True

    return False


def get_charset(content_type):
    if not content_type:
        return DEFAULT_CHARSET

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


logger = logging.getLogger('revproxy.cookies')


def cookie_from_string(cookie_string):
    """Parser for HTTP header set-cookie
    The return from this function will be used as parameters for
    django's response.set_cookie method. Because set_cookie doesn't
    have parameter comment, this cookie attribute will be ignored.

    """

    valid_attrs = ('path', 'domain', 'comment', 'expires',
                   'max_age', 'httponly', 'secure')

    cookie_dict = {}

    cookie_parts = cookie_string.split(';')
    try:
        cookie_dict['key'], cookie_dict['value'] = cookie_parts[0].split('=')
    except ValueError:
        logger.warning('Invalid cookie: `%s`', cookie_string)
        return None

    for part in cookie_parts[1:]:
        if '=' in part:
            try:
                attr, value = part.split('=')
            except ValueError:
                logger.warning('Invalid cookie attribute: `%s`', part)
                continue

            value = value.strip()
        else:
            attr = part
            value = ''

        attr = attr.strip().lower()
        if not attr:
            continue

        if attr in valid_attrs:
            if attr in ('httponly', 'secure'):
                cookie_dict[attr] = True
            elif attr in 'comment':
                # ignoring comment attr as explained in the
                #   function docstring
                continue
            else:
                cookie_dict[attr] = value
        else:
            logger.warning('Unknown cookie attribute %s', attr)

    return cookie_dict
