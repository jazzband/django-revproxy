import sys

if sys.version_info >= (3, 0, 0):
    from urllib.response import addinfourl
else:
    from urllib import addinfourl

from io import BytesIO


# got to prefix str with b since str and byte are different in Python 3
# https://docs.python.org/3/reference/lexical_analysis.html#strings
def response_like_factory(proxy_request, headers, retcode,
                          content=b'Fake file'):

    def get_response_like_object(proxy_request):
        fp_like = BytesIO(content)

        url = proxy_request.get_full_url()
        return addinfourl(fp_like, headers, url, retcode)

    return get_response_like_object
