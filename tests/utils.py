# -*- coding: utf-8 -*-

import urllib3

from io import BytesIO

from mock import MagicMock, Mock

from revproxy.views import ProxyView

DEFAULT_BODY_CONTENT = u'áéíóú'.encode('utf-8')
URLOPEN = 'urllib3.PoolManager.urlopen'


class CustomProxyView(ProxyView):
    upstream = "http://www.example.com"
    diazo_rules = None


def get_urlopen_mock(body=DEFAULT_BODY_CONTENT, headers=dict(),
                     status=200, cookie=set()):
    mockHttpResponse = Mock(name='httplib.HTTPResponse')
    mockHttpResponse.msg.getheaders.return_value = cookie

    if not hasattr(body, 'read'):
        body = BytesIO(body)

    else:
        body.seek(0)

    urllib3_response = urllib3.HTTPResponse(body,
                                            headers,
                                            status,
                                            preload_content=False,
                                            original_response=mockHttpResponse)

    return MagicMock(return_value=urllib3_response)


class MockFile():

    def __init__(self, content):
        self.content = content
        self.mock_file = BytesIO(content)
        self.mock_read_size = 4

    def closed(self):
        return self.mock_file.closed

    def close(self):
        self.mock_file.close()

    def read(self, size=-1):
        return self.mock_file.read(self.mock_read_size)

    def seek(self, size):
        return self.mock_file.seek(size)
