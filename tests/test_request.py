
import sys

if sys.version_info >= (3, 0, 0):
    from urllib.parse import parse_qs
else:
    from urlparse import parse_qs

from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase, RequestFactory

from mock import patch

from urllib3 import Retry

from revproxy.views import ProxyView

from .utils import get_urlopen_mock


class RequestTest(TestCase):

    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='jacob', email='jacob@example.com', password='top_secret')

        urlopen_mock = get_urlopen_mock()
        self.urlopen_patcher = patch('urllib3.PoolManager.urlopen',
                                     urlopen_mock)

        self.urlopen = self.urlopen_patcher.start()

    def tearDown(self):
        self.urlopen_patcher.stop()

    def test_default_add_remote_user_attr(self):
        proxy_view = ProxyView()
        self.assertFalse(proxy_view.add_remote_user)

    def factory_custom_proxy_view(self, **kwargs):
        class CustomProxyView(ProxyView):
            add_remote_user = kwargs.get('add_remote_user', False)
            upstream = kwargs.get('upstream', 'http://www.example.com')
            retries = kwargs.get('retries', None)
            rewrite = kwargs.get('rewrite', tuple())

        if kwargs.get('method') == 'POST':
            request = self.factory.post(kwargs.get('path', ''),
                                        kwargs.get('post_data', {}))
        elif kwargs.get('method') == 'PUT':
            request = self.factory.put('path', kwargs.get('request_data', {}))
        else:
            request = self.factory.get(kwargs.get('path', ''),
                                       kwargs.get('get_data', {}))

        if kwargs.get('anonymous'):
            request.user = AnonymousUser()
        else:
            request.user = self.user

        if kwargs.get('headers'):
            for key, value in kwargs.get('headers').items():
                request.META[key] = value

        response = CustomProxyView.as_view()(request, kwargs.get('path', ''))
        return {'request': request, 'response': response}

    def test_remote_user_authenticated(self):
        options = {'add_remote_user': True, 'anonymous': False,
                   'path': 'test'}

        self.factory_custom_proxy_view(**options)
        url = 'http://www.example.com/test'
        headers = {'REMOTE_USER': 'jacob', 'Cookie': ''}
        self.urlopen.assert_called_with('GET', url,
                                        redirect=False,
                                        retries=None,
                                        preload_content=False,
                                        decode_content=False,
                                        headers=headers,
                                        body=b'')

    def test_remote_user_anonymous(self):
        options = {'add_remote_user': True, 'anonymous': True,
                   'path': 'test/anonymous/'}

        self.factory_custom_proxy_view(**options)
        url = 'http://www.example.com/test/anonymous/'
        headers = {'Cookie': ''}
        self.urlopen.assert_called_with('GET', url, redirect=False,
                                        retries=None,
                                        preload_content=False,
                                        decode_content=False,
                                        headers=headers, body=b'')

    def test_custom_retries(self):
        RETRIES = Retry(20, backoff_factor=0.1)
        options = {'path': 'test/', 'retries': RETRIES}

        self.factory_custom_proxy_view(**options)
        url = 'http://www.example.com/test/'
        headers = {'Cookie': ''}
        self.urlopen.assert_called_with('GET', url, redirect=False,
                                        retries=RETRIES,
                                        preload_content=False,
                                        decode_content=False,
                                        headers=headers, body=b'')

    def test_simple_get(self):
        get_data = {'a': ['b'], 'c': ['d'], 'e': ['f']}
        options = {'path': 'test/', 'get_data': get_data}

        self.factory_custom_proxy_view(**options)

        assert self.urlopen.called
        called_qs = self.urlopen.call_args[0][1].split('?')[-1]
        called_get_data = parse_qs(called_qs)
        self.assertEqual(called_get_data, get_data)

    def test_get_with_attr_list(self):
        get_data = {
            u'a': [u'a', u'b', u'c', u'd'],
            u'foo': [u'bar'],
        }
        options = {'path': '/', 'get_data': get_data}
        self.factory_custom_proxy_view(**options)

        assert self.urlopen.called
        called_qs = self.urlopen.call_args[0][1].split('?')[-1]

        called_get_data = parse_qs(called_qs)
        self.assertEqual(called_get_data, get_data)

    def test_post_and_get(self):
        get_data = {'x': ['y', 'z']}
        post_data = {'a': ['b'], 'c': ['d'], 'e': ['f']}

        options = {'path': '/?x=y&x=z', 'post_data': post_data}
        result = self.factory_custom_proxy_view(**options)

        assert self.urlopen.called
        called_qs = self.urlopen.call_args[0][1].split('?')[-1]

        # Check for GET data
        called_get_data = parse_qs(called_qs)
        self.assertEqual(called_get_data, get_data)

        # Check for POST data
        self.assertEqual(self.urlopen.call_args[1]['body'],
                         result.get('request').body)

    def test_put(self):
        request_data = {'a': ['b'], 'c': ['d'], 'e': ['f']}

        options = {'path': '/', 'method': 'PUT', 'request_data': request_data}

        result = self.factory_custom_proxy_view(**options)

        assert self.urlopen.called

        # Check for request data
        self.assertEqual(self.urlopen.call_args[1]['body'],
                         result.get('request').body)

        self.assertEqual(self.urlopen.call_args[0][0], 'PUT')

    def test_simple_rewrite(self):
        rewrite = (
            (r'^/yellow/star/?$', r'/black/hole/'),
            (r'^/foo/$', r'/bar'),
        )
        options = {'path': '/yellow/star', 'add_remote_user': False,
                   'rewrite': rewrite}

        result = self.factory_custom_proxy_view(**options)
        self.assertEqual(result.get('response').url, '/black/hole/')
        self.assertEqual(result.get('response').status_code, 302)

    def test_rewrite_with_get(self):
        rewrite = (
            (r'^/foo/(.*)$', r'/bar\1'),
        )
        get_data = {'a': ['1'], 'b': ['c']}
        options = {'path': '/foo/', 'add_remote_user': False,
                   'rewrite': rewrite, 'get_data': get_data}

        result = self.factory_custom_proxy_view(**options)
        path, querystring = result.get('response').url.split('?')
        self.assertEqual(path, '/bar')
        self.assertEqual(result.get('response').status_code, 302)

        response_data = parse_qs(querystring)
        self.assertEqual(response_data, get_data)

    def test_rewrite_to_external_location(self):
        rewrite = (
            (r'^/yellow/star/?$', r'http://www.mozilla.org/'),
        )
        options = {'path': '/yellow/star', 'add_remote_user': False,
                   'rewrite': rewrite}

        result = self.factory_custom_proxy_view(**options)
        self.assertEqual(result.get('response').url, 'http://www.mozilla.org/')
        self.assertEqual(result.get('response').status_code, 302)

    def test_rewrite_to_view_name(self):
        rewrite = (
            (r'^/yellow/star/$', r'login'),
        )
        options = {'path': '/yellow/star/', 'add_remote_user': False,
                   'rewrite': rewrite}

        result = self.factory_custom_proxy_view(**options)
        self.assertEqual(result.get('response').url, '/accounts/login/')
        self.assertEqual(result.get('response').status_code, 302)

    def test_no_rewrite(self):
        rewrite = (
            (r'^/yellow/star/$', r'login'),
            (r'^/foo/(.*)$', r'/bar\1'),
        )

        options = {'path': 'test/', 'rewrite': rewrite}

        result = self.factory_custom_proxy_view(**options)
        url = 'http://www.example.com/test/'
        headers = {'Cookie': ''}
        self.urlopen.assert_called_with('GET', url, redirect=False,
                                        retries=None,
                                        preload_content=False,
                                        decode_content=False,
                                        headers=headers, body=b'')

    def test_remote_user_injection_anonymous(self):
        request_headers = {'HTTP_REMOTE_USER': 'foo'}
        options = {'path': 'test', 'anonymous': True,
                   'headers': request_headers}
        result = self.factory_custom_proxy_view(**options)

        url = 'http://www.example.com/test'
        headers = {'Cookie': ''}
        self.urlopen.assert_called_with('GET', url,
                                        redirect=False,
                                        retries=None,
                                        preload_content=False,
                                        decode_content=False,
                                        headers=headers,
                                        body=b'')

    def test_remote_user_injection_authenticated(self):
        request_headers = {'HTTP_REMOTE_USER': 'foo'}
        options = {'path': 'test', 'headers': request_headers}
        result = self.factory_custom_proxy_view(**options)

        url = 'http://www.example.com/test'
        headers = {'Cookie': ''}
        self.urlopen.assert_called_with('GET', url,
                                        redirect=False,
                                        retries=None,
                                        preload_content=False,
                                        decode_content=False,
                                        headers=headers,
                                        body=b'')

    def test_remote_user_injection_authenticated_add_remote_user(self):
        request_headers = {'HTTP_REMOTE_USER': 'foo'}
        options = {'path': 'test', 'headers': request_headers,
                   'add_remote_user': True}
        result = self.factory_custom_proxy_view(**options)

        url = 'http://www.example.com/test'
        headers = {'Cookie': '', 'REMOTE_USER': 'jacob'}
        self.urlopen.assert_called_with('GET', url,
                                        redirect=False,
                                        retries=None,
                                        preload_content=False,
                                        decode_content=False,
                                        headers=headers,
                                        body=b'')

    def test_remote_user_injection_anonymous_add_remote_user(self):
        request_headers = {'HTTP_REMOTE_USER': 'foo'}
        options = {'path': 'test', 'headers': request_headers,
                   'add_remote_user': True, 'anonymous': True}
        result = self.factory_custom_proxy_view(**options)

        url = 'http://www.example.com/test'
        headers = {'Cookie': ''}
        self.urlopen.assert_called_with('GET', url,
                                        redirect=False,
                                        retries=None,
                                        preload_content=False,
                                        decode_content=False,
                                        headers=headers,
                                        body=b'')
