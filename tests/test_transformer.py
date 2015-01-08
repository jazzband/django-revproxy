
from mock import patch

from django.test import RequestFactory, TestCase

from revproxy.views import ProxyView

from .utils import get_urlopen_mock


URLOPEN = 'urllib3.PoolManager.urlopen'


class CustomProxyView(ProxyView):
    upstream = "http://www.example.com"


class TransformerTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def tearDown(self):
        CustomProxyView.upstream = "http://www.example.com"

    def test_no_diazo(self):
        pass

    def test_ajax_request(self):
        request = self.factory.get('/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        urlopen_mock = get_urlopen_mock()
        with patch(URLOPEN, urlopen_mock):
            response = CustomProxyView.as_view()(request, '/')

        self.assertEqual(response.content, b'Mock')

    def test_response_streaming(self):
        # TODO: We actually don't support stream proxy so far
        pass

    def test_no_content_type(self):
        request = self.factory.get('/')

        urlopen_mock = get_urlopen_mock()
        with patch(URLOPEN, urlopen_mock):
            response = CustomProxyView.as_view()(request, '/')

        self.assertEqual(response.content, b'Mock')

    def test_unsupported_content_type(self):
        request = self.factory.get('/')
        headers = {'Content-Type': 'application/pdf'}

        urlopen_mock = get_urlopen_mock(headers=headers)
        with patch(URLOPEN, urlopen_mock):
            response = CustomProxyView.as_view()(request, '/')

        self.assertEqual(response.content, b'Mock')

    def test_unsupported_content_encoding_zip(self):
        request = self.factory.get('/')
        headers = {
            'Content-Encoding': 'zip',
            'Content-Type': 'text/html',
        }

        urlopen_mock = get_urlopen_mock(headers=headers)
        with patch(URLOPEN, urlopen_mock):
            response = CustomProxyView.as_view()(request, '/')

        self.assertEqual(response.content, b'Mock')

    def test_unsupported_content_encoding_deflate(self):
        request = self.factory.get('/')
        headers = {
            'Content-Encoding': 'deflate',
            'Content-Type': 'text/html',
        }

        urlopen_mock = get_urlopen_mock(headers=headers)
        with patch(URLOPEN, urlopen_mock):
            response = CustomProxyView.as_view()(request, '/')

        self.assertEqual(response.content, b'Mock')

    def test_unsupported_content_encoding_compress(self):
        request = self.factory.get('/')
        headers = {
            'Content-Encoding': 'compress',
            'Content-Type': 'text/html',
        }

        urlopen_mock = get_urlopen_mock(headers=headers)
        with patch(URLOPEN, urlopen_mock):
            response = CustomProxyView.as_view()(request, '/')

        self.assertEqual(response.content, b'Mock')

    def test_server_redirection_status(self):
        request = self.factory.get('/')
        headers = {'Content-Type': 'text/html'}

        urlopen_mock = get_urlopen_mock(headers=headers, status=301)
        with patch(URLOPEN, urlopen_mock):
            response = CustomProxyView.as_view()(request, '/')

        self.assertEqual(response.content, b'Mock')

    def test_no_content_status(self):
        request = self.factory.get('/')
        headers = {'Content-Type': 'text/html'}

        urlopen_mock = get_urlopen_mock(headers=headers, status=204)
        with patch(URLOPEN, urlopen_mock):
            response = CustomProxyView.as_view()(request, '/')

        self.assertEqual(response.content, b'Mock')

    def test_response_length_zero(self):
        request = self.factory.get('/')
        headers = {'Content-Type': 'text/html'}

        urlopen_mock = get_urlopen_mock(b'', headers, 200)
        with patch(URLOPEN, urlopen_mock):
            response = CustomProxyView.as_view()(request, '/')

        self.assertEqual(response.content, b'')

    def test_transform(self):
        request = self.factory.get('/')
        content = b'<div class="test-transform">testing</div>'
        headers = {'Content-Type': 'text/html'}

        urlopen_mock = get_urlopen_mock(content, headers)
        with patch(URLOPEN, urlopen_mock):
            response = CustomProxyView.as_view(
                diazo_theme_template='diazo.html'
            )(request, '/')

        self.assertNotIn(content, response.content)

    def test_html5_transform(self):
        request = self.factory.get('/')
        content = b'test'
        headers = {'Content-Type': 'text/html'}

        urlopen_mock = get_urlopen_mock(content, headers)
        with patch(URLOPEN, urlopen_mock):
            response = CustomProxyView.as_view(html5=True)(request, '/')

        self.assertIn(b'<!DOCTYPE html>', response.content)
