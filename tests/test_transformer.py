
import codecs

from mock import patch

from django.test import RequestFactory, TestCase

from revproxy.views import ProxyView

from .utils import get_urlopen_mock, DEFAULT_BODY_CONTENT


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

    def test_disable_request_header(self):
        request = self.factory.get('/', HTTP_X_DIAZO_OFF='true')
        headers = {'Content-Type': 'text/html'}
        urlopen_mock = get_urlopen_mock(headers=headers)

        with patch(URLOPEN, urlopen_mock):
            response = CustomProxyView.as_view()(request, '/')

        self.assertEqual(response.content, DEFAULT_BODY_CONTENT)

    def test_disable_response_header(self):
        request = self.factory.get('/')
        headers = {'Content-Type': 'text/html', 'X-Diazo-Off': 'true'}
        urlopen_mock = get_urlopen_mock(headers=headers)

        with patch(URLOPEN, urlopen_mock):
            response = CustomProxyView.as_view()(request, '/')

        self.assertEqual(response.content, DEFAULT_BODY_CONTENT)

    def test_x_diazo_off_false_on_response(self):
        request = self.factory.get('/')
        headers = {'Content-Type': 'text/html', 'X-Diazo-Off': 'false'}
        urlopen_mock = get_urlopen_mock(headers=headers)

        with patch(URLOPEN, urlopen_mock):
            response = CustomProxyView.as_view()(request, '/')

        self.assertNotIn(response.content, DEFAULT_BODY_CONTENT)

    def test_x_diazo_off_invalid(self):
        request = self.factory.get('/')
        headers = {'Content-Type': 'text/html', 'X-Diazo-Off': 'nopz'}
        urlopen_mock = get_urlopen_mock(headers=headers)

        with patch(URLOPEN, urlopen_mock), self.assertRaises(ValueError):
            CustomProxyView.as_view()(request, '/')

    def test_ajax_request(self):
        request = self.factory.get('/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        headers = {'Content-Type': 'text/html'}

        urlopen_mock = get_urlopen_mock(headers=headers)
        with patch(URLOPEN, urlopen_mock):
            response = CustomProxyView.as_view()(request, '/')

        self.assertEqual(response.content, DEFAULT_BODY_CONTENT)

    def test_response_streaming(self):
        request = self.factory.get('/')
        urlopen_mock = get_urlopen_mock()

        with patch(URLOPEN, urlopen_mock):
            response = CustomProxyView.as_view()(request, '/')

        content = b''.join(response.streaming_content)
        self.assertEqual(content, DEFAULT_BODY_CONTENT)

    def test_response_reading_of_file_stream(self):
        request = self.factory.get('/')
        file_stream = codecs.open("./tests/test_files/file_1",encoding='utf-8')
        original_content = file_stream.read().encode('utf-8')

        file_stream.seek(0) # returns pointer to begin of file
        urlopen_mock = get_urlopen_mock(file_stream)

        with patch(URLOPEN, urlopen_mock):
            response = CustomProxyView.as_view()(request, '/')

        content = b''.join(response.streaming_content)

        self.assertEqual(original_content, content)

        file_stream.close()

    def test_no_content_type(self):
        request = self.factory.get('/')
        headers = {'Content-Length': '1'}

        urlopen_mock = get_urlopen_mock(headers=headers)
        with patch(URLOPEN, urlopen_mock):
            response = CustomProxyView.as_view()(request, '/')

        self.assertEqual(response.content, DEFAULT_BODY_CONTENT)

    def test_unsupported_content_type(self):
        request = self.factory.get('/')
        headers = {'Content-Type': 'application/pdf',
                   'Content-Length': '1'}

        urlopen_mock = get_urlopen_mock(headers=headers)
        with patch(URLOPEN, urlopen_mock):
            response = CustomProxyView.as_view()(request, '/')

        self.assertEqual(response.content, DEFAULT_BODY_CONTENT)

    def test_unsupported_content_encoding_zip(self):
        request = self.factory.get('/')
        headers = {
            'Content-Encoding': 'zip',
            'Content-Type': 'text/html',
        }

        urlopen_mock = get_urlopen_mock(headers=headers)
        with patch(URLOPEN, urlopen_mock):
            response = CustomProxyView.as_view()(request, '/')

        self.assertEqual(response.content, DEFAULT_BODY_CONTENT)

    def test_unsupported_content_encoding_compress(self):
        request = self.factory.get('/')
        headers = {
            'Content-Encoding': 'compress',
            'Content-Type': 'text/html',
        }

        urlopen_mock = get_urlopen_mock(headers=headers)
        with patch(URLOPEN, urlopen_mock):
            response = CustomProxyView.as_view()(request, '/')

        self.assertEqual(response.content, DEFAULT_BODY_CONTENT)

    def test_server_redirection_status(self):
        request = self.factory.get('/')
        headers = {'Content-Type': 'text/html'}

        urlopen_mock = get_urlopen_mock(headers=headers, status=301)
        with patch(URLOPEN, urlopen_mock):
            response = CustomProxyView.as_view()(request, '/')

        self.assertEqual(response.content, DEFAULT_BODY_CONTENT)

    def test_no_content_status(self):
        request = self.factory.get('/')
        headers = {'Content-Type': 'text/html'}

        urlopen_mock = get_urlopen_mock(headers=headers, status=204)
        with patch(URLOPEN, urlopen_mock):
            response = CustomProxyView.as_view()(request, '/')

        self.assertEqual(response.content, DEFAULT_BODY_CONTENT)

    def test_response_length_zero(self):
        request = self.factory.get('/')
        headers = {'Content-Type': 'text/html'}

        urlopen_mock = get_urlopen_mock(u''.encode('utf-8'), headers, 200)
        with patch(URLOPEN, urlopen_mock):
            response = CustomProxyView.as_view()(request, '/')

        self.assertEqual(response.content, b'')

    def test_transform(self):
        request = self.factory.get('/')
        content = u'<div class="test-transform">testing</div>'.encode('utf-8')
        headers = {'Content-Type': 'text/html'}

        urlopen_mock = get_urlopen_mock(content, headers)
        with patch(URLOPEN, urlopen_mock):
            response = CustomProxyView.as_view(
                diazo_theme_template='diazo.html'
            )(request, '/')

        self.assertNotIn(content, response.content)

    def test_html5_transform(self):
        request = self.factory.get('/')
        content = u'test'.encode('utf-8')
        headers = {'Content-Type': 'text/html'}

        urlopen_mock = get_urlopen_mock(content, headers)
        with patch(URLOPEN, urlopen_mock):
            response = CustomProxyView.as_view(html5=True)(request, '/')

        self.assertIn(b'<!DOCTYPE html>', response.content)
