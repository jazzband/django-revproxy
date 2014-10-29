

import os

from django.test import TestCase

from revproxy.views import ProxyView


class ViewTest(TestCase):

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
