# -*- coding: utf-8 -*-

from sys import version_info

import codecs

from mock import patch, MagicMock, PropertyMock

from django.test import RequestFactory, TestCase

from revproxy.views import ProxyView

from revproxy.transformer import asbool

from .utils import get_urlopen_mock, DEFAULT_BODY_CONTENT, MockFile, URLOPEN


CONTENT = """`1234567890-=qwertyuiop[]\\asdfghjkl;'zxcvbnm,./
˜!@#$%ˆ&*()_+QWTYUIOP{}|ASDFGHJKL:"ZXCVBNM<>?
`¡™£¢∞§¶•ªº–≠œ∑´®†\“‘«åß∂ƒ©˙∆˚¬…æΩ≈ç√∫˜µ≤≥÷
áéíóúÁÉÍÓÚàèìòùÀÈÌÒÙäëïöüÄËÏÖÜãõÃÕçÇ"""

if version_info >= (3, 0, 0):
    FILE_CONTENT = bytes(CONTENT, 'utf-8')
else:
    FILE_CONTENT = CONTENT


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

        test_file = MockFile(FILE_CONTENT)
        mock_file = MagicMock()
        type(mock_file).encoding = PropertyMock(return_value='utf-8')
        type(mock_file).closed = PropertyMock(side_effect=test_file.closed)
        mock_file.read.side_effect = test_file.read
        mock_file.close.side_effect = test_file.close
        mock_file.seek.side_effect = test_file.seek

        urlopen_mock = get_urlopen_mock(mock_file)

        with patch(URLOPEN, urlopen_mock):
            response = CustomProxyView.as_view()(request, '/')

        content = b''.join(response.streaming_content)

        self.assertEqual(FILE_CONTENT, content)

    def test_num_reads_by_stream_on_a_file(self):
        request = self.factory.get('/')

        # number of reads done by the stream.
        # it must be said that the stream reads the file one last time before
        # closing the file.For further information look at the file named
        # response.py on library urlib3, method read.
        NUM_READS = 69

        test_file = MockFile(FILE_CONTENT)

        mock_file = MagicMock()
        type(mock_file).encoding = PropertyMock(return_value='utf-8')
        type(mock_file).closed = PropertyMock(side_effect=test_file.closed)
        mock_file.read.side_effect = test_file.read
        mock_file.close.side_effect = test_file.close
        mock_file.seek.side_effect = test_file.seek

        urlopen_mock = get_urlopen_mock(mock_file)

        with patch(URLOPEN, urlopen_mock):
            response = CustomProxyView.as_view()(request, '/')

        content = b''.join(response.streaming_content)
        self.assertEqual(mock_file.read.call_count, NUM_READS)
        self.assertEqual(FILE_CONTENT, content)

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

    def test_asbool(self):
        test_true = ['true', 'yes', 'on', 'y', 't', '1']
        for element in test_true:
            self.assertEqual(True, asbool(element))

        test_false = ['false', 'no', 'off', 'n', 'f', '0']
        for element in test_false:
            self.assertEqual(False, asbool(element))

        self.assertEqual(True, asbool(1))
        self.assertEqual(False, asbool(0))
        with self.assertRaises(ValueError):
            asbool('test')
