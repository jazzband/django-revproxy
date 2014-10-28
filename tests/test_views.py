
import os
import sys

if sys.version_info >= (3, 0, 0):
    from urllib.parse import parse_qs
else:
    from urlparse import parse_qs

from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase, RequestFactory

from mock import patch

from revproxy.views import ProxyView


class SimpleTest(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='jacob', email='jacob@example.com', password='top_secret')

        self.urllib2_Request_patcher = patch('revproxy.views.Request')
        self.urllib2_urlopen_patcher = patch('revproxy.views.urlopen')

        self.urllib2_Request = self.urllib2_Request_patcher.start()
        self.urllib2_urlopen = self.urllib2_urlopen_patcher.start()

    def tearDown(self):
        self.urllib2_Request_patcher.stop()
        self.urllib2_urlopen_patcher.stop()

    def test_upstream_not_implemented(self):
        proxy_view = ProxyView()
        with self.assertRaises(NotImplementedError):
            upstream = proxy_view.upstream

    def test_upstream_overriden(self):
        class CustomProxyView(ProxyView):
            upstream = 'http://www.google.com/'

        proxy_view = CustomProxyView()
        self.assertEqual(proxy_view.upstream, 'http://www.google.com/')


    def test_default_diazo_rules(self):
        class CustomProxyView(ProxyView):
            pass

        proxy_view = CustomProxyView()

        correct_path = os.path.join(os.path.dirname(__file__), 'diazo.xml')
        self.assertEqual(proxy_view.diazo_rules, correct_path)

    def test_diazo_rules_overriden(self):
        class CustomProxyView(ProxyView):
            diazo_rules = '/tmp/diazo.xml'

        proxy_view = CustomProxyView()
        self.assertEqual(proxy_view.diazo_rules, '/tmp/diazo.xml')

    def test_default_diazo_theme_template(self):
        proxy_view = ProxyView()
        self.assertEqual(proxy_view.diazo_theme_template, 'diazo.html')

    def test_default_html_attr(self):
        proxy_view = ProxyView()
        self.assertFalse(proxy_view.html5)

    def test_default_add_remote_user_attr(self):
        proxy_view = ProxyView()
        self.assertFalse(proxy_view.add_remote_user)

    def test_remote_user_authenticated(self):
        class CustomProxyView(ProxyView):
            add_remote_user = True
            upstream = 'http://www.example.com'

        request = self.factory.get('/')
        request.user = self.user

        response = CustomProxyView.as_view()(request, '/test')

        request_url = 'http://www.example.com/test'
        request_headers = {'REMOTE_USER': 'jacob', u'Cookie': u''}
        self.urllib2_Request.assert_called_with(request_url,
                                                headers=request_headers)

    def test_remote_user_anonymous(self):
        class CustomProxyView(ProxyView):
            add_remote_user = True
            upstream = 'http://www.example.com'

        request = self.factory.get('/')
        request.user = AnonymousUser()

        response = CustomProxyView.as_view()(request, '/test/anonymous/')

        request_url = 'http://www.example.com/test/anonymous/'
        request_headers = {u'Cookie': u''}
        self.urllib2_Request.assert_called_with(request_url,
                                                headers=request_headers)

    def test_simple_get(self):
        class CustomProxyView(ProxyView):
            upstream = 'http://www.example.com'

        get_data = {'a': ['b'], 'c': ['d'], 'e': ['f']}
        request = self.factory.get('/', get_data)
        response = CustomProxyView.as_view()(request, '/')

        assert self.urllib2_Request.called

        called_qs = self.urllib2_Request.call_args[0][0].split('?')[-1]
        called_get_data = parse_qs(called_qs)
        self.assertEqual(called_get_data, get_data)


    def test_get_with_attr_list(self):
        class CustomProxyView(ProxyView):
            upstream = 'http://www.example.com'

        get_data = {
            u'a': [u'a', u'b', u'c', u'd'],
            u'foo': [u'bar'],
        }
        request = self.factory.get('/', get_data)
        response = CustomProxyView.as_view()(request, '/')

        assert self.urllib2_Request.called
        called_qs = self.urllib2_Request.call_args[0][0].split('?')[-1]

        called_get_data = parse_qs(called_qs)
        self.assertEqual(called_get_data, get_data)
