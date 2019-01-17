
from django.test import TestCase

from mock import PropertyMock

from revproxy import utils

from .utils import get_urlopen_mock, CustomProxyView

from django.test import RequestFactory


class UtilsTest(TestCase):
    def test_get_charset(self):
        content_type = 'text/html; charset=utf-8'
        charset = utils.get_charset(content_type)
        self.assertEqual(charset, 'utf-8')

    def test_get_default_charset(self):
        content_type = ''
        charset = utils.get_charset(content_type)
        self.assertEqual('latin-1', charset)

    def test_required_header(self):
        self.assertTrue(utils.required_header('HTTP_USER_AGENT'))
        self.assertTrue(utils.required_header('HTTP_ANY_THING_AFTER_HTTP'))

    def test_ignore_host_header(self):
        self.assertFalse(utils.required_header('HTTP_HOST'))
        self.assertFalse(utils.required_header('HTTP_REMOTE_USER'))
        self.assertFalse(utils.required_header('HTTP_ACCEPT_ENCODING'))
        self.assertFalse(utils.required_header('WRONG_HEADER'))

    def test_ignore_accept_encoding_header(self):
        self.assertFalse(utils.required_header('HTTP_ACCEPT_ENCODING'))

    def test_is_html_content_type(self):
        self.assertEqual(True, utils.is_html_content_type("text/html"))
        self.assertEqual(True,
                         utils.is_html_content_type('application/xhtml+xml'))

    def test_is_not_html_content_type(self):
        self.assertEqual(False, utils.is_html_content_type("html/text"))
        self.assertEqual(False,
                         utils.is_html_content_type('application/pdf'))

    def test_not_should_stream(self):
        SMALLER_THAN_MIN_STREAMING_LENGTH = '5'
        headers = {'Content-Type': 'text/html',
                   'Content-Length': SMALLER_THAN_MIN_STREAMING_LENGTH}

        urlopen_mock = get_urlopen_mock(headers=headers)

        type(urlopen_mock).headers = PropertyMock(return_value=headers)
        self.assertEqual(False, utils.should_stream(urlopen_mock))

        headers['Content-Type'] = 'application/pdf'
        type(urlopen_mock).headers = PropertyMock(return_value=headers)
        self.assertEqual(False, utils.should_stream(urlopen_mock))

    def test_should_be_stream(self):
        BIGGER_THAN_MIN_STREAMING_LENGTH = '5120'
        headers = {'Content-Type': 'application/pdf',
                   'Content-Length': 'asad'}

        urlopen_mock = get_urlopen_mock(headers=headers)

        type(urlopen_mock).headers = PropertyMock(return_value=headers)
        self.assertEqual(True, utils.should_stream(urlopen_mock))

        headers['Content-Length'] = BIGGER_THAN_MIN_STREAMING_LENGTH
        type(urlopen_mock).headers = PropertyMock(return_value=headers)
        self.assertEqual(True, utils.should_stream(urlopen_mock))

    def test_strict_cookies(self):
        valid_cookie = '_cookie_session="1234c12d4p=312341243";' \
                       'expires=Thu, 29 Jan 2015 13:51:41 GMT; httponly;' \
                       'secure;Path=/gitlab'
        self.assertDictContainsSubset(
            {
                'expires': 'Thu, 29 Jan 2015 13:51:41 GMT',
                'value': '1234c12d4p=312341243',
            },
            utils.cookie_from_string(valid_cookie, strict_cookies=True),
        )

        invalid_cookie = "_cookie_session:xyz"
        self.assertIsNone(utils.cookie_from_string(invalid_cookie,
                                                   strict_cookies=True))

    def test_quoted_value_cookies(self):
        valid_cookie = '_cookie_session="1234c12d4p=312341243";' \
                       'expires=Thu, 29 Jan 2015 13:51:41 GMT; httponly;' \
                       'secure;Path="/gitlab"'
        self.assertDictContainsSubset(
            {
                'expires': 'Thu, 29 Jan 2015 13:51:41 GMT',
                'value': '1234c12d4p=312341243',
                'path': '/gitlab',
            },
            utils.cookie_from_string(valid_cookie),
        )

    def test_get_dict_in_cookie_from_string(self):
        cookie = "_cookie_session = 1266bb13c139cfba3ed1c9c68110bae9;" \
                 "expires=Thu, 29 Jan 2015 13:51:41 -0000; httponly;" \
                 "Path=/gitlab"

        my_dict = utils.cookie_from_string(cookie)
        self.assertIs(type(my_dict), dict)

    def test_valid_attr_in_cookie_from_string(self):
        cookie = "_cookie_session=1266bb13c139cfba3ed1c9c68110bae9;" \
                 "expires=Thu, 29 Jan 2015 13:51:41 -0000; httponly;" \
                 "secure;Path=/gitlab"

        self.assertIn('path', utils.cookie_from_string(cookie))
        self.assertIn('/', utils.cookie_from_string(cookie)['path'])

        self.assertIn('expires', utils.cookie_from_string(cookie))
        self.assertIn('Thu, 29 Jan 2015 13:51:41 -0000',
                      utils.cookie_from_string(cookie)['expires'])

        self.assertIn('httponly', utils.cookie_from_string(cookie))
        self.assertTrue(utils.cookie_from_string(cookie)['httponly'])

        self.assertIn('secure', utils.cookie_from_string(cookie))
        self.assertTrue(utils.cookie_from_string(cookie)['secure'])

        self.assertIn('value', utils.cookie_from_string(cookie))
        self.assertIn('1266bb13c139cfba3ed1c9c68110bae9',
                      utils.cookie_from_string(cookie)['value'])

        self.assertIn('key', utils.cookie_from_string(cookie))
        self.assertIn('_cookie_session',
                      utils.cookie_from_string(cookie)['key'])

    def test_None_value_cookie_from_string(self):
        cookie = "_cookie_session="
        self.assertIn('_cookie_session',
                      utils.cookie_from_string(cookie)['key'])
        self.assertIn('',
                      utils.cookie_from_string(cookie)['value'])

    def test_invalid_cookie_from_string(self):
        cookie = "_cookie_session1234c12d4p312341243"
        self.assertIsNone(utils.cookie_from_string(cookie))

        cookie = "_cookie_session==1234c12d4p312341243"
        self.assertIsNone(utils.cookie_from_string(cookie))

        cookie = "_cookie_session:123s234c1234d12"
        self.assertIsNone(utils.cookie_from_string(cookie))

    def test_invalid_attr_cookie_from_string(self):
        cookie = "_cookie=2j3d4k35f466l7fj9;path=/;None;"

        self.assertNotIn('None', utils.cookie_from_string(cookie))

        self.assertIn('value', utils.cookie_from_string(cookie))
        self.assertIn('2j3d4k35f466l7fj9',
                      utils.cookie_from_string(cookie)['value'])

        self.assertIn('key', utils.cookie_from_string(cookie))
        self.assertIn('_cookie',
                      utils.cookie_from_string(cookie)['key'])

        self.assertIn('path', utils.cookie_from_string(cookie))
        self.assertIn('/', utils.cookie_from_string(cookie)['path'])

    def test_ignore_comment_cookie_from_string(self):
        cookie = "_cookie=k2j3l;path=/;comment=this is a new comment;secure"
        self.assertNotIn('comment', utils.cookie_from_string(cookie))

    def test_value_exeption_cookie_from_string(self):
        cookie = "_cookie=k2j3l;path=/,comment=teste;httponly"
        self.assertIsNotNone(utils.cookie_from_string(cookie))
