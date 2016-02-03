import mock

from django.test import TestCase
from urllib3.poolmanager import SSL_KEYWORDS

from revproxy import connection, pool


mock_http_pool = mock.Mock(wraps=connection.HTTPConnectionPool)


class TestPoolManager(TestCase):

    def test_new_pool(self):
        new_pool = pool.PoolManager()._new_pool('https', 'example.com', '443')
        self.assertIsInstance(new_pool, connection.HTTPSConnectionPool)

    @mock.patch('revproxy.pool.pool_classes_by_scheme', {'http': mock_http_pool})
    def test_new_http_pool(self):
        example_ssl_key = SSL_KEYWORDS[0]
        mock_non_ssl_key = 'mock_keyword'
        mock_non_ssl_value = 'mock non-ssl value'
        mock_host_and_port = ('example.com', '80')

        pool_manager = pool.PoolManager()
        pool_manager.connection_pool_kw.update({
            example_ssl_key: 'mock ssl value',
            mock_non_ssl_key: mock_non_ssl_value,
        })
        new_pool = pool_manager._new_pool('http', *mock_host_and_port)

        mock_http_pool.assert_called_once_with(
            *mock_host_and_port,
            **{mock_non_ssl_key: mock_non_ssl_value}
        )
