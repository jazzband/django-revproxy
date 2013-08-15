
import urllib
import urllib2
from urlparse import urljoin

from django.views.decorators.csrf import csrf_exempt

from .response import HttpProxyResponse
from .utils import normalize_headers, NoHTTPRedirectHandler


@csrf_exempt
def proxy(request, path, base_url):

    request_headers = normalize_headers(request)

    if request.user and request.user.is_active:
        request_headers['REMOTE_USER'] = request.user.username

    request_url = urljoin(base_url, path)
    proxy_request = urllib2.Request(request_url, headers=request_headers)

    data = request.POST.items()
    if data:
        proxy_request.add_data(urllib.urlencode(data))


    opener = urllib2.build_opener(NoHTTPRedirectHandler)
    urllib2.install_opener(opener)

    try:
        proxy_response = urllib2.urlopen(proxy_request)
    except urllib2.HTTPError as e:
        proxy_response = e

    return HttpProxyResponse(proxy_response)

