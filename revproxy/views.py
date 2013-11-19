# -*- coding: utf-8 -*-

import urllib
import urllib2
from urlparse import urljoin, urlparse

from django.conf import settings
from django.views.generic import View
from django.utils.decorators import classonlymethod

from .response import HttpProxyResponse
from .utils import normalize_headers, NoHTTPRedirectHandler, encode_items
from .transformer import DiazoTransformer


class ProxyView(View):
    base_url = None
    add_remote_user = False
    diazo_rules = None
    diazo_theme_template = None
    html5 = False

    @classonlymethod
    def as_view(cls, **initkwargs):
        view = super(ProxyView, cls).as_view(**initkwargs)
        view.csrf_exempt = True
        return view

    def dispatch(self, request, path):
        request_payload = request.body
        request_headers = normalize_headers(request)

        if self.add_remote_user and request.user.is_active:
            request_headers['REMOTE_USER'] = request.user.username

        request_url = urljoin(
            self.base_url,
            urllib2.quote(path.encode('utf8'))
        )

        if request.GET:
            items = encode_items(request.GET.items())
            request_url += '?' + urllib.urlencode(items)

        proxy_request = urllib2.Request(request_url, headers=request_headers)

        if request.POST:
            if 'multipart/form-data' in request_headers.get('Content-Type', ''):
                proxy_request.add_data(request_payload)
            else:
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
            if request.is_secure():
                location = 'https://' + location
            else:
                location = 'http://' + location

            proxy_response.headers['Location'] = location

        response = HttpProxyResponse(proxy_response)

        if self.diazo_rules and self.diazo_theme_template:
            diazo = DiazoTransformer(request, response)
            response = diazo.transform(self.diazo_rules,
                                       self.diazo_theme_template,
                                       self.html5)

        return response
