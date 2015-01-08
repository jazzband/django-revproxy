
from mock import MagicMock
from urllib3 import HTTPResponse


def get_urlopen_mock(body=b'Mock', headers=dict(), status=200):
    return MagicMock(return_value=HTTPResponse(body, headers, status))
