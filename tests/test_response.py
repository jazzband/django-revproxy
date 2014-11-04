from django.test import RequestFactory, TestCase
from json import dumps as json_dumps

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

        path = "/example"
        content_type = 'application/json; charset=%s' % DEFAULT_CHARSET
        request = self.factory.post(path, json_dumps({'lala' : 'lalala'}), content_type=content_type)

        proxy_response = response_like_factory(request, self.headers, 200)

        self.urllib2_urlopen_patcher = patch('revproxy.views.urlopen', new=proxy_response)
        self.urllib2_urlopen = self.urllib2_urlopen_patcher.start()

        response = CustomProxyView.as_view()(request, path)

        charset = get_charset(response['Content-Type'])

        self.assertEquals(DEFAULT_CHARSET, charset)

        self.urllib2_urlopen_patcher.stop()

    def test_charset_is_not_default_charset(self):
        class CustomProxyView(ProxyView):
            upstream = "http://www.example.com"

        path = "/example"
        request = self.factory.get(path)

        proxy_response = response_like_factory(request, self.headers, 200)

        self.urllib2_urlopen_patcher = patch('revproxy.views.urlopen', new=proxy_response)
        self.urllib2_urlopen = self.urllib2_urlopen_patcher.start()

        response = CustomProxyView.as_view()(request, path)

        charset = get_charset(response['Content-Type'])

        self.assertNotEquals(DEFAULT_CHARSET, charset)

        self.urllib2_urlopen_patcher.stop()

    def test_location_not_in_headers(self):
        class CustomProxyView(ProxyView):
            upstream = "http://www.example.com"

        self.headers = {'Location' : '/'}
        path = "/path"
        request = self.factory.get(path)

        proxy_response = response_like_factory(request, self.headers, 200)

        self.urllib2_urlopen_patcher = patch('revproxy.views.urlopen', new=proxy_response)
        self.urllib2_urlopen = self.urllib2_urlopen_patcher.start()

        response = CustomProxyView.as_view()(request, path)

        response = self.factory.get('/',CONTENT_TYPE=utf8_content_type)
        http_response = CustomProxyView.as_view()(response, '/')
        self.urllib2_urlopen_patcher.stop()
