from json import dumps as json_dumps

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

    def test_charset_is_default_charset(self):
        class CustomProxyView(ProxyView):
            upstream = "http://www.example.com"

        path = "/"
        content_type = 'application/json; charset=%s' % DEFAULT_CHARSET
        request = self.factory.post(
            path,
            json_dumps({'lala': 'lalala'}),
            content_type=content_type
            )

        proxy_response = response_like_factory(request, request.META, 200)

        self.urllib2_urlopen_patcher = patch(
            'revproxy.views.urlopen',
            new=proxy_response
            )
        self.urllib2_urlopen = self.urllib2_urlopen_patcher.start()

        response = CustomProxyView.as_view()(request, path)

        charset = get_charset(response['Content-Type'])

        self.assertEquals(DEFAULT_CHARSET, charset)

        self.urllib2_urlopen_patcher.stop()

    def test_charset_is_not_default_charset(self):
        class CustomProxyView(ProxyView):
            upstream = "http://www.example.com"

        path = "/"
        request = self.factory.get(path)

        proxy_response = response_like_factory(request, self.headers, 200)

        self.urllib2_urlopen_patcher = patch(
            'revproxy.views.urlopen',
            new=proxy_response
            )
        self.urllib2_urlopen = self.urllib2_urlopen_patcher.start()

        response = CustomProxyView.as_view()(request, path)

        charset = get_charset(response['Content-Type'])

        self.assertNotEquals(DEFAULT_CHARSET, charset)

        self.urllib2_urlopen_patcher.stop()

    def test_location_replaces_request_host(self):
        class CustomProxyView(ProxyView):
            upstream = "http://www.example.com"

        self.headers = {'Location': 'http://www.example.com'}
        path = "/path"
        request = self.factory.get(path)

        proxy_response = response_like_factory(request, self.headers, 200)

        self.urllib2_urlopen_patcher = patch(
            'revproxy.views.urlopen',
            new=proxy_response
            )
        self.urllib2_urlopen = self.urllib2_urlopen_patcher.start()

        response = CustomProxyView.as_view()(request, path)
        location = "http://" + request.get_host()

        self.assertEquals(location, response['Location'])

        self.urllib2_urlopen_patcher.stop()

    def test_location_replaces_secure_request_host(self):
        class CustomProxyView(ProxyView):
            upstream = "https://www.example.com"

        self.headers = {'Location': 'https://www.example.com'}
        path = "/path"
        request = self.factory.get(path, secure=True)

        proxy_response = response_like_factory(request, self.headers, 200)

        self.urllib2_urlopen_patcher = patch(
            'revproxy.views.urlopen',
            new=proxy_response
            )
        self.urllib2_urlopen = self.urllib2_urlopen_patcher.start()

        response = CustomProxyView.as_view()(request, path)

        location = "https://" + request.get_host()

        self.assertEquals(location, response['Location'])

        self.urllib2_urlopen_patcher.stop()
