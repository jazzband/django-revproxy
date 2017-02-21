
from urllib3.connection import HTTPConnection, HTTPSConnection
from urllib3.connectionpool import HTTPConnectionPool, HTTPSConnectionPool


def _output(self, s):
    """Host header should always be first"""

    if s.lower().startswith(b'host: '):
        self._buffer.insert(1, s)
    else:
        self._buffer.append(s)


HTTPConnectionPool.ConnectionCls = type(
    'RevProxyHTTPConnection',
    (HTTPConnection,),
    {'_output': _output},
)

HTTPSConnectionPool.ConnectionCls = type(
    'RevProxyHTTPSConnection',
    (HTTPSConnection,),
    {'_output': _output}
)
