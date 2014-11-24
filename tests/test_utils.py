
import sys

if sys.version_info >= (3, 0, 0):  # pragma: no cover
    from urllib.request import HTTPRedirectHandler
else:  # pragma: no cover
    # Fallback to Python 2.7
    from urllib2 import HTTPRedirectHandler

from django.test import TestCase

from revproxy import utils


class UtilsTest(TestCase):

    def test_get_charset(self):
        content_type = 'text/html; charset=utf-8'
        charset = utils.get_charset(content_type)
        self.assertEqual(charset, 'utf-8')

    def test_required_header(self):
        self.assertTrue(utils.required_header('HTTP_REMOTE_USER'))

    def test_ignore_host_header(self):
        self.assertFalse(utils.required_header('HTTP_HOST'))

    def test_ignore_accept_encoding_header(self):
        self.assertFalse(utils.required_header('HTTP_ACCEPT_ENCODING'))

    def test_NoHTTPRedirectHandler(self):
        assert issubclass(utils.NoHTTPRedirectHandler, HTTPRedirectHandler)
        handler = utils.NoHTTPRedirectHandler()
        self.assertIsNone(handler.redirect_request())
