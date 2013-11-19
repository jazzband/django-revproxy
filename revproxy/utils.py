
import urllib2
from urlparse import urlparse


class NoHTTPRedirectHandler(urllib2.HTTPRedirectHandler, object):
    def redirect_request(self, *args, **kwargs):
        return None


class ConditionalHTTPRedirectHandler(urllib2.HTTPRedirectHandler, object):

    def redirect_request(self, *args, **kwargs):
        """Only perform a redirect in case it is to the same host than
        the original requests.

        Example 1:
            Original request: http://domain.com/
            Redirect response: http://domain.com/search

            domain.com == domain.com, so perform the redirect.

        Example 2:
            Original request: http://domain.com/
            Redirect response: http://domain.org/

            domain.com != domain.org, so just send the redirect
            response as a result and let the client decide what
            to do.

        """

        newurl = kwargs.get('newurl', args[-1])
        req = kwargs.get('req', args[0])
        url_parsed = urlparse(newurl)

        if url_parsed.netloc == req.host:
            return super(ConditionalHTTPRedirectHandler, self)\
                                    .redirect_request(*args, **kwargs)


IGNORE_HEADERS = (
    'HTTP_ACCEPT_ENCODING', # We want content to be uncompressed so
                            #   we remove the Accept-Encoding from
                            #   original request
    'HTTP_HOST',
)


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
    for key, value in items:
        encoded.append((key.encode('utf-8'), value.encode('utf-8')))
    return encoded
