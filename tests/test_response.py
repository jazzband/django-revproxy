#! *-* coding: utf8 *-*

import logging

import urllib3

from wsgiref.util import is_hop_by_hop

from django.test import RequestFactory, TestCase
from mock import MagicMock, patch
from urllib3.exceptions import HTTPError

from .utils import (get_urlopen_mock, DEFAULT_BODY_CONTENT,
                    CustomProxyView, URLOPEN)


class ResponseTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.log = logging.getLogger('revproxy')
        self.log.disabled = True

    def tearDown(self):
        CustomProxyView.upstream = "http://www.example.com"
        CustomProxyView.diazo_rules = None
        self.log.disabled = False

    def test_broken_response(self):
        request = self.factory.get('/')

        urlopen_mock = MagicMock(side_effect=HTTPError())
        with patch(URLOPEN, urlopen_mock), self.assertRaises(HTTPError):
            CustomProxyView.as_view()(request, '/')

    def test_location_replaces_request_host(self):
        headers = {'Location': 'http://www.example.com'}
        path = "/path"
        request = self.factory.get(path)

        urlopen_mock = get_urlopen_mock(headers=headers)
        with patch(URLOPEN, urlopen_mock):
            response = CustomProxyView.as_view()(request, path)

        location = "http://" + request.get_host()
        self.assertEqual(location, response['Location'])

    def test_location_replaces_secure_request_host(self):
        CustomProxyView.upstream = "https://www.example.com"

        headers = {'Location': 'https://www.example.com'}
        path = "/path"
        request = self.factory.get(
            path,
            # using kwargs instead of the secure parameter because it
            #   works only after Django 1.7
            **{
                'wsgi.url_scheme': 'https'  # tell factory to use
            }                               # https over http
        )

        urlopen_mock = get_urlopen_mock(headers=headers)
        with patch(URLOPEN, urlopen_mock):
            response = CustomProxyView.as_view()(request, path)

        location = "https://" + request.get_host()
        self.assertEqual(location, response['Location'])

    def test_response_headers_are_not_in_hop_by_hop_headers(self):
        path = "/"
        request = self.factory.get(path)
        headers = {
            'connection': '0',
            'proxy-authorization': 'allow',
            'content-type': 'text/html',
        }

        urlopen_mock = get_urlopen_mock(headers=headers)
        with patch(URLOPEN, urlopen_mock):
            response = CustomProxyView.as_view()(request, path)

        # Django 3.2+
        if hasattr(response, 'headers'):
            response_headers = response.headers
        else:
            response_headers = response._headers

        for header in response_headers:
            self.assertFalse(is_hop_by_hop(header))

    def test_response_code_remains_the_same(self):
        path = "/"
        request = self.factory.get(path)
        status = 300

        urlopen_mock = get_urlopen_mock(status=status)
        with patch(URLOPEN, urlopen_mock):
            response = CustomProxyView.as_view()(request, path)

        self.assertEqual(response.status_code, status)

    def test_response_content_remains_the_same(self):
        path = "/"
        request = self.factory.get(path)
        status = 300

        headers = {'Content-Type': 'text/html'}
        urlopen_mock = get_urlopen_mock(DEFAULT_BODY_CONTENT, headers, status)
        with patch(URLOPEN, urlopen_mock):
            response = CustomProxyView.as_view()(request, path)

        # had to prefix it with 'b' because Python 3 treats str and byte
        # differently
        self.assertEqual(DEFAULT_BODY_CONTENT, response.content)

    def test_cookie_is_not_in_response_headers(self):
        path = "/"
        request = self.factory.get(path)
        headers = {
            'connection': '0',
            'proxy-authorization': 'allow',
            'content-type': 'text/html',
            'set-cookie':   '_cookie=9as8sd32fg48gh2j4k7o3;path=/'
        }

        urlopen_mock = get_urlopen_mock(headers=headers)
        with patch(URLOPEN, urlopen_mock):
            response = CustomProxyView.as_view()(request, path)

        # Django 3.2+
        if hasattr(response, 'headers'):
            response_headers = response.headers
        else:
            response_headers = response._headers
        self.assertNotIn('set-cookie', response_headers)

    def test_set_cookie_is_used_by_httpproxy_response(self):
        path = "/"
        request = self.factory.get(path)
        headers = urllib3.response.HTTPHeaderDict({
            'connection': '0',
            'proxy-authorization': 'allow',
            'content-type': 'text/html'
        })
        headers.add('set-cookie', '_cookie1=l4hs3kdf2jsh2324')
        headers.add('set-cookie', '_cookie2=l2lk5sj3df22sk3j4')

        urlopen_mock = get_urlopen_mock(headers=headers)
        with patch(URLOPEN, urlopen_mock):
            response = CustomProxyView.as_view()(request, path)

        self.assertIn("_cookie1", response.cookies.keys())
        self.assertIn("_cookie2", response.cookies.keys())

    def test_invalid_cookie(self):
        path = "/"
        request = self.factory.get(path)
        headers = {
            'connection': '0',
            'proxy-authorization': 'allow',
            'content-type': 'text/html',
            'set-cookie':   'invalid-cookie',
        }

        urlopen_mock = get_urlopen_mock(headers=headers)
        with patch(URLOPEN, urlopen_mock):
            response = CustomProxyView.as_view()(request, path)

        # Django 3.2+
        if hasattr(response, 'headers'):
            response_headers = response.headers
        else:
            response_headers = response._headers
        self.assertFalse(response.cookies)
