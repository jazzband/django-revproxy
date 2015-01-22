
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

        cookie = "_cookie_session=;path=/"

    def test_invalid_cookie_from_string(self):
        cookie = "_cookie_session1234c12d4p312341243"
        self.assertIsNone(utils.cookie_from_string(cookie))

        cookie = "_cookie_session==1234c12d4p312341243"
        self.assertIsNone(utils.cookie_from_string(cookie))

        cookie = "_cookie_session:123s234c1234d12"
        self.assertIsNone(utils.cookie_from_string(cookie))

