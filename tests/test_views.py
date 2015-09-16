
from mock import patch

import os

from django.test import TestCase, RequestFactory
from django.utils.six.moves.urllib.parse import ParseResult

from revproxy.exceptions import InvalidUpstream
from revproxy.views import ProxyView, DiazoProxyView

from .utils import get_urlopen_mock


class ViewTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        urlopen_mock = get_urlopen_mock()
        self.urlopen_patcher = patch('urllib3.PoolManager.urlopen',
                                     urlopen_mock)
        self.urlopen = self.urlopen_patcher.start()

    def test_connection_pool_singleton(self):
        view1 = ProxyView()
        view2 = ProxyView()
        self.assertIs(view1.http, view2.http)

    @patch('revproxy.transformer.DiazoTransformer.transform')
    def test_set_diazo_as_argument(self, transform):
        url = 'http://example.com/'
        rules = '/tmp/diazo.xml'
        path = '/'

        class CustomProxyView(DiazoProxyView):
            upstream = url

        view = CustomProxyView.as_view(diazo_rules='/tmp/diazo.xml')
        request = self.factory.get(path)
        view(request, path)

        self.assertEqual(transform.call_args[0][0], rules)

    def test_set_upstream_as_argument(self):
        url = 'http://example.com/'
        view = ProxyView.as_view(upstream=url)

        request = self.factory.get('/')
        response = view(request, '/')

        headers = {u'Cookie': u''}
        self.urlopen.assert_called_with('GET', url,
                                        body=b'',
                                        redirect=False,
                                        retries=None,
                                        preload_content=False,
                                        decode_content=False,
                                        headers=headers)

    def test_upstream_not_implemented(self):
        proxy_view = ProxyView()
        with self.assertRaises(NotImplementedError):
            upstream = proxy_view.upstream

    def test_upstream_parsed_url_cache(self):
        class CustomProxyView(ProxyView):
            upstream = 'http://www.example.com'

        proxy_view = CustomProxyView()
        with self.assertRaises(AttributeError):
            proxy_view._parsed_url

        # Test for parsed URL
        proxy_view.get_upstream('')
        self.assertIsInstance(proxy_view._parsed_url, ParseResult)
        # Get parsed URL from cache
        proxy_view.get_upstream('')
        self.assertIsInstance(proxy_view._parsed_url, ParseResult)

    def test_upstream_without_scheme(self):
        class BrokenProxyView(ProxyView):
            upstream = 'www.example.com'

        proxy_view = BrokenProxyView()
        with self.assertRaises(InvalidUpstream):
            proxy_view.get_upstream('')

    def test_upstream_overriden(self):
        class CustomProxyView(ProxyView):
            upstream = 'http://www.google.com/'

        proxy_view = CustomProxyView()
        self.assertEqual(proxy_view.upstream, 'http://www.google.com/')

    def test_upstream_without_trailing_slash(self):
        class CustomProxyView(ProxyView):
            upstream = 'http://example.com/area'

        request = self.factory.get('login')
        CustomProxyView.as_view()(request, 'login')

        headers = {u'Cookie': u''}
        self.urlopen.assert_called_with('GET', 'http://example.com/area/login',
                                        body=b'',
                                        redirect=False,
                                        retries=None,
                                        preload_content=False,
                                        decode_content=False,
                                        headers=headers)

    def test_default_diazo_rules(self):
        class CustomProxyView(DiazoProxyView):
            pass

        proxy_view = CustomProxyView()

        correct_path = os.path.join(os.path.dirname(__file__), 'diazo.xml')
        self.assertEqual(proxy_view.diazo_rules, correct_path)

    def test_diazo_rules_overriden(self):
        class CustomProxyView(DiazoProxyView):
            diazo_rules = '/tmp/diazo.xml'

        proxy_view = CustomProxyView()
        self.assertEqual(proxy_view.diazo_rules, '/tmp/diazo.xml')

    def test_default_diazo_theme_template(self):
        proxy_view = DiazoProxyView()
        self.assertEqual(proxy_view.diazo_theme_template, 'diazo.html')

    def test_default_html_attr(self):
        proxy_view = DiazoProxyView()
        self.assertFalse(proxy_view.html5)

    def test_default_add_remote_user_attr(self):
        proxy_view = DiazoProxyView()
        self.assertFalse(proxy_view.add_remote_user)

    def test_inheritance_context_mixin(self):
        mixin_view = DiazoProxyView()
        self.assertTrue(hasattr(mixin_view, 'get_context_data'))

    def test_added_view_context(self):
        class CustomProxyView(DiazoProxyView):
            def get_context_data(self, **kwargs):
                context_data = {'key': 'value'}
                context_data.update(kwargs)
                return super(CustomProxyView, self).get_context_data(**context_data)

        class TextGetContextData(CustomProxyView):
            def get_context_data(self, **kwargs):
                context_data = super(CustomProxyView, self).get_context_data(**context_data)
                self.assertEqual(context_data['key'], 'value')
                return {}


    def test_tilde_is_not_escaped(self):
        class CustomProxyView(ProxyView):
            upstream = 'http://example.com'

        request = self.factory.get('/~')
        CustomProxyView.as_view()(request, '/~')

        url = 'http://example.com/~'
        headers = {u'Cookie': u''}
        self.urlopen.assert_called_with('GET', url,
                                        body=b'',
                                        redirect=False,
                                        retries=None,
                                        preload_content=False,
                                        decode_content=False,
                                        headers=headers)

    def test_space_is_escaped(self):
        class CustomProxyView(ProxyView):
            upstream = 'http://example.com'

        path = '/ test test'
        request = self.factory.get(path)
        CustomProxyView.as_view()(request, path)

        url = 'http://example.com/+test+test'
        headers = {u'Cookie': u''}
        self.urlopen.assert_called_with('GET', url,
                                        body=b'',
                                        redirect=False,
                                        retries=None,
                                        preload_content=False,
                                        decode_content=False,
                                        headers=headers)

    def test_extending_headers(self):
        class CustomProxyView(ProxyView):
            upstream = 'http://example.com'

            def get_proxy_request_headers(self, request):
                headers = super(CustomProxyView, self).\
                                get_proxy_request_headers(request)
                headers['DNT'] = 1
                return headers

        path = '/'
        request = self.factory.get(path)
        CustomProxyView.as_view()(request, path)

        url = 'http://example.com/'
        headers = {u'Cookie': u''}
        custom_headers = {'DNT': 1}
        custom_headers.update(headers)
        self.urlopen.assert_called_with('GET', url,
                                        body=b'',
                                        redirect=False,
                                        retries=None,
                                        preload_content=False,
                                        decode_content=False,
                                        headers=custom_headers)
