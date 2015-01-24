
import urllib3

from io import StringIO

from mock import MagicMock, Mock


def get_urlopen_mock(body=u'Mock', headers=dict(), status=200, cookie=set()):
    mockHttpResponse = Mock(name='httplib.HTTPResponse')
    mockHttpResponse.msg.getheaders.return_value = cookie

    urllib3_response = urllib3.HTTPResponse(StringIO(body),
                                            headers,
                                            status,
                                            preload_content=False,
                                            original_response=mockHttpResponse)

    return MagicMock(return_value=urllib3_response)
