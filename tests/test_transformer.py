
from mock import patch

from django.test import RequestFactory, TestCase

from revproxy.views import ProxyView

from .utils import response_like_factory


class CustomProxyView(ProxyView):
    upstream = "http://www.example.com"


class CustomProxyViewTransformed(ProxyView):
    upstream = "http://www.example.com"
    html5 = True
    diazo_theme_template = 'diazo.html'


class TransformerTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def tearDown(self):
        CustomProxyView.upstream = "http://www.example.com"

    def test_no_diazo(self):
        pass

    def test_ajax_request(self):
        request = self.factory.get('/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        get_proxy_response = response_like_factory(request, {}, 200)

        patcher = patch(
            'revproxy.views.urlopen',
            new=get_proxy_response
        )
        with patcher:
            response = CustomProxyView.as_view()(request, '/')
            self.assertEqual(response.content, b'Fake file')

    def test_response_streaming(self):
        # TODO: We actually don't support stream proxy so far
        pass

    def test_no_content_type(self):
        request = self.factory.get('/')
        get_proxy_response = response_like_factory(request, {}, 200)

        patcher = patch('revproxy.views.urlopen', new=get_proxy_response)
        with patcher:
            response = CustomProxyView.as_view()(request, '/')
            self.assertEqual(response.content, b'Fake file')

    def test_unsupported_content_type(self):
        request = self.factory.get('/')
        headers = {'Content-Type': 'application/pdf'}
        get_proxy_response = response_like_factory(request, headers, 200)

        patcher = patch(
            'revproxy.views.urlopen',
            new=get_proxy_response
        )
        with patcher:
            response = CustomProxyView.as_view()(request, '/')
            self.assertEqual(response.content, b'Fake file')

    def test_unsupported_content_encoding_zip(self):
        request = self.factory.get('/')
        headers = {
            'Content-Encoding': 'zip',
            'Content-Type': 'text/html',
        }
        get_proxy_response = response_like_factory(request, headers, 200)

        patcher = patch(
            'revproxy.views.urlopen',
            new=get_proxy_response
        )
        with patcher:
            response = CustomProxyView.as_view()(request, '/')
            self.assertEqual(response.content, b'Fake file')

    def test_unsupported_content_encoding_deflate(self):
        request = self.factory.get('/')
        headers = {
            'Content-Encoding': 'deflate',
            'Content-Type': 'text/html',
        }
        get_proxy_response = response_like_factory(request, headers, 200)

        patcher = patch(
            'revproxy.views.urlopen',
            new=get_proxy_response
        )
        with patcher:
            response = CustomProxyView.as_view()(request, '/')
            self.assertEqual(response.content, b'Fake file')

    def test_unsupported_content_encoding_compress(self):
        request = self.factory.get('/')
        headers = {
            'Content-Encoding': 'compress',
            'Content-Type': 'text/html',
        }
        get_proxy_response = response_like_factory(request, headers, 200)

        patcher = patch(
            'revproxy.views.urlopen',
            new=get_proxy_response
        )
        with patcher:
            response = CustomProxyView.as_view()(request, '/')
            self.assertEqual(response.content, b'Fake file')

    def test_server_redirection_status(self):
        request = self.factory.get('/')
        headers = {'Content-Type': 'text/html'}
        get_proxy_response = response_like_factory(request, headers, 301)

        patcher = patch(
            'revproxy.views.urlopen',
            new=get_proxy_response
        )
        with patcher:
            response = CustomProxyView.as_view()(request, '/')
            self.assertEqual(response.content, b'Fake file')

    def test_no_content_status(self):
        request = self.factory.get('/')
        headers = {'Content-Type': 'text/html'}
        get_proxy_response = response_like_factory(request, headers, 204)

        patcher = patch(
            'revproxy.views.urlopen',
            new=get_proxy_response
        )
        with patcher:
            response = CustomProxyView.as_view()(request, '/')
            self.assertEqual(response.content, b'Fake file')

    def test_response_length_zero(self):
        request = self.factory.get('/')
        content = b''
        headers = {'Content-Type': 'text/html'}
        get_proxy_response = response_like_factory(request, headers,
                                                   200, content)

        patcher = patch(
            'revproxy.views.urlopen',
            new=get_proxy_response
        )
        with patcher:
            response = CustomProxyView.as_view()(request, '/')
            self.assertEqual(response.content, content)

    def test_transform(self):
        request = self.factory.get('/')
        content = b'<div class="test-transform">testing</div>'
        headers = {'Content-Type': 'text/html'}

        get_proxy_response = response_like_factory(request, headers, 200, content)

        patcher = patch(
            'revproxy.views.urlopen',
            new=get_proxy_response
        )
        with patcher:
            response = CustomProxyViewTransformed.as_view()(request, '/')
            self.assertNotIn(content, response.content)

    def test_html5_transform(self):
        pass
