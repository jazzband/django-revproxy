from django.test import TestCase, RequestFactory
from revproxy.response import HttpProxyResponse

from mock import patch

from urllib2 import urlopen, Request

from revproxy.views import ProxyView
from revproxy.utils import DEFAULT_CHARSET


class ResponseTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.urllib2_urlopen_patcher = patch('revproxy.views.urlopen')
        self.response_patcher = patch('revproxy.views.HttpProxyResponse')

        self.urllib2_urlopen = self.urllib2_urlopen_patcher.start()
        self.responser = self.response_patcher.start()


    def tearDown(self):
        self.urllib2_urlopen_patcher.stop()
        self.responser = self.response_patcher.stop()

    def test_unicode_content_is_not_none(self):
        class CustomProxyView(ProxyView):
            upstream = 'http://www.example.com'

        request = self.factory.get('/')
        response = CustomProxyView.as_view()(request, '/')

        self.assertIsNotNone(response.unicode_content)

    def test_charset_is_default_charset(self):
        class CustomProxyView(ProxyView):
            upstream = 'http://www.example.com'

        utf8_content_type = 'text/html'

        response = self.factory.get('/',CONTENT_TYPE=utf8_content_type)
        http_response = CustomProxyView.as_view()(response, '/')
    
         
