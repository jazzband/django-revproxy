
import urllib
import urllib2
from urlparse import urljoin, urlparse

from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from .response import HttpProxyResponse
from .utils import normalize_headers, NoHTTPRedirectHandler
from .transformer import DiazoTransformer


class ProxyView(View):
    base_url = None
    add_remote_user = False
    diazo_rules = None
    diazo_theme_template = None
    html5 = False

    @csrf_exempt
    def dispatch(self, request, path):
        request_headers = normalize_headers(request)

        if self.add_remote_user and request.user.is_active:
            request_headers['REMOTE_USER'] = request.user.username

        request_url = urljoin(self.base_url, urllib2.quote(path))

        if request.GET:
            request_url += '?' + urllib.urlencode(request.GET.items())

        proxy_request = urllib2.Request(request_url, headers=request_headers)

        if request.POST:
            post_data = request.POST.items()
            proxy_request.add_data(urllib.urlencode(post_data))

        opener = urllib2.build_opener(NoHTTPRedirectHandler)
        urllib2.install_opener(opener)

        try:
            proxy_response = urllib2.urlopen(proxy_request)
        except urllib2.HTTPError as e:
            proxy_response = e

        location = proxy_response.headers.get('Location')
        if location and location.startswith(location):
            location = location.replace(self.base_url.strip('/'),
                                        request.get_host())
            proxy_response.headers['Location'] = location

        response = HttpProxyResponse(proxy_response)

        if self.diazo_rules and self.diazo_theme_template:
            diazo = DiazoTransformer(request, response)
            response = diazo.transform(self.diazo_rules,
                                       self.diazo_theme_template,
                                       self.html5)

        return response
