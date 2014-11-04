import sys

if sys.version_info >= (3, 0, 0):
    from urllib.response import addinfourl
else:
    from urllib import addinfourl

from io import BytesIO


def response_like_factory(proxy_request, headers, retcode):
    def get_response_like_object(proxy_request):
        fp_like = BytesIO('Fake file')

        url = proxy_request.get_full_url()
        return addinfourl(fp_like, headers, url, retcode)

    return get_response_like_object
