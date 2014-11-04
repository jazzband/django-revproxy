
if sys.version_info >= (3, 0, 0):
    from urllib.response import addinfourl
else:
    from urllib import addinfourl

from io import StringIO


def response_like_factory(proxy_request, headers, retcode):
    def get_response_like_object(proxy_request):
        fp_like = StringIO('Fake file')

        url = proxy_request.get_full_url()
        return addinfourl(fp_like, headers, url, retcode)

    return get_response_like_object


#proxy_response = response_like_factory(proxy_request, headers, retcode)
#patch('revproxy.views.urlopen', new=proxy_response)
