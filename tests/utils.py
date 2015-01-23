
from mock import MagicMock, Mock
from urllib3 import HTTPResponse


def get_urlopen_mock(body=b'Mock', headers=dict(), status=200, cookie=set()):
    mockHttpResponse = Mock(name='httplib.HTTPResponse')
    mockHttpResponse.msg.getheaders.return_value = cookie
    return MagicMock(return_value=HTTPResponse(body, headers, status,
                     original_response=mockHttpResponse))
