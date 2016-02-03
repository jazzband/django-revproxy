from django.test import TestCase

from revproxy import connection


class TestOutput(TestCase):

    def setUp(self):
        self.connection = connection.HTTPConnectionPool.ConnectionCls('example.com')

    def test_byte_url(self):
        """Output strings are always byte strings, even using Python 3"""
        mock_output = b'mock output'
        connection._output(self.connection, mock_output)
        self.assertEqual(self.connection._buffer, [mock_output])

    def test_host_is_first(self):
        """Make sure the host line is second in the request"""
        mock_host_output = b'host: example.com'
        for output in [b'GET / HTTP/1.1', b'before', mock_host_output, b'after']:
            connection._output(self.connection, output)
        self.assertEqual(self.connection._buffer[1], mock_host_output)
