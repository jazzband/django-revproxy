# -*- coding: utf-8 -*-

import urllib3

from io import BytesIO

from mock import MagicMock, Mock

DEFAULT_BODY_CONTENT = u'áéíóú'.encode('utf-8')


def get_urlopen_mock(body=DEFAULT_BODY_CONTENT, headers=dict(),
                     status=200, cookie=set()):
    mockHttpResponse = Mock(name='httplib.HTTPResponse')
    mockHttpResponse.msg.getheaders.return_value = cookie

    print body

    if not hasattr(body,'read'): 
        print 'IF'
        body = BytesIO(body)

    else:
        print 'ELSE'
        print body.read()
        body.seek(0)

    urllib3_response = urllib3.HTTPResponse(body,
                                            headers,
                                            status,
                                            preload_content=False,
                                            original_response=mockHttpResponse)

    return MagicMock(return_value=urllib3_response)
