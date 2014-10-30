from django.test import TestCase
from revproxy.response import HttpProxyResponse

from urllib2 import urlopen, Request


class ResponseTest(TestCase):
    def setUp(self):
        proxy_request = Request('http://www.example.com')
        self.proxy_response = urlopen(proxy_request)

    def test_unicode_content_is_not_none(self):
        self.proxy_response.headers['Content-Type'] = "text/html; charset=UTF-8"
        response = HttpProxyResponse(self.proxy_response)

        self.assertIsNotNone(response.unicode_content)

    def test_unicode_content_is_none(self):
        self.proxy_response.headers['Content-Type'] = "text/html;"
        response = HttpProxyResponse(self.proxy_response)

        self.assertIsNone(response.unicode_content)

