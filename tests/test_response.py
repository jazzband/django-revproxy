import sys

if sys.version_info >= (3, 0, 0):
    from urllib.request import Request, urlopen
else:
    # Fallback to Python 2.7
    from urllib2 import Request, urlopen

from django.test import RequestFactory, TestCase
from mock import patch
from revproxy.utils import DEFAULT_CHARSET, get_charset
from revproxy.views import ProxyView

from .utils import response_like_factory


class ResponseTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.urllib2_Request_patcher = patch('revproxy.views.Request')

        self.urllib2_Request = self.urllib2_Request_patcher.start()
        self.headers = {}

    def tearDown(self):
        self.urllib2_Request_patcher.stop()
        self.headers = {}

    def test_charset_is_not_default_charset(self):
        class CustomProxyView(ProxyView):
            upstream = "http://www.example.com"

        path = "/"
        request = self.factory.get(path)

        get_proxy_response = response_like_factory(request, self.headers, 200)

        urllib2_urlopen_patcher = patch(
            'revproxy.views.urlopen',
            new=get_proxy_response
            )
        with urllib2_urlopen_patcher:
            response = CustomProxyView.as_view()(request, path)
            charset = get_charset(response['Content-Type'])
            self.assertNotEquals(DEFAULT_CHARSET, charset)

    def test_location_replaces_request_host(self):
        class CustomProxyView(ProxyView):
            upstream = "http://www.example.com"

        self.headers = {'Location': 'http://www.example.com'}
        path = "/path"
        request = self.factory.get(path)

        get_proxy_response = response_like_factory(request, self.headers, 200)

        urllib2_urlopen_patcher = patch(
            'revproxy.views.urlopen',
            new=get_proxy_response
            )
        with urllib2_urlopen_patcher:
            response = CustomProxyView.as_view()(request, path)
            location = "http://" + request.get_host()
            self.assertEquals(location, response['Location'])

    def test_location_replaces_secure_request_host(self):
        class CustomProxyView(ProxyView):
            upstream = "https://www.example.com"

        self.headers = {'Location': 'https://www.example.com'}
        path = "/path"
        request = self.factory.get(
            path,
            # using kwargs instead of the secure parameter because it works only
            # after Django 1.7
            **{
                'wsgi.url_scheme': 'https'  # tell factory to use https over http
                }
            )

        get_proxy_response = response_like_factory(request, self.headers, 200)

        urllib2_urlopen_patcher = patch(
            'revproxy.views.urlopen',
            new=get_proxy_response
            )
        with urllib2_urlopen_patcher:
            response = CustomProxyView.as_view()(request, path)
            location = "https://" + request.get_host()
            self.assertEquals(location, response['Location'])

    def test_request(self):
        class CustomProxyView(ProxyView):
            upstream = "http://www.example.com"

        path = "/"
        request = self.factory.get(path)
        get_proxy_response = response_like_factory(request, self.headers, 200)

        urllib2_urlopen_patcher = patch(
            'revproxy.views.urlopen',
            new=get_proxy_response
            )

        with urllib2_urlopen_patcher:
            response = CustomProxyView.as_view()(request, path)
