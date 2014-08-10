# -*- coding: utf-8 -*-

import urllib
import urllib2
from urlparse import urljoin, urlparse

from django.views.generic import View
from django.utils.decorators import classonlymethod

from .response import HttpProxyResponse
from .utils import normalize_headers, NoHTTPRedirectHandler, encode_items
from .transformer import DiazoTransformer

SUPPORTED_FORM_TYPES = ['multipart/form-data', 'application/octet-stream']


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

        if request_headers.get('Content-Type', '') in SUPPORTED_FORM_TYPES:
            proxy_request.add_data(request_payload)

        if request.POST:
            encoded = ""
            for (key, value) in request.POST.lists():
                parsed = {}
                if len(value) > 1:
                    for subvalue in value:
                        parsed[key] = subvalue
                        encoded += urllib.urlencode(parsed) + "&"
                else:
                    parsed[key] = value[0]
                    encoded += urllib.urlencode(parsed) + "&"
            proxy_request.add_data(encoded[:-1])

        opener = urllib2.build_opener(NoHTTPRedirectHandler)
        urllib2.install_opener(opener)

        try:
            proxy_response = urllib2.urlopen(proxy_request)
        except urllib2.HTTPError as e:
            proxy_response = e

        location = proxy_response.headers.get('Location')
        if location:
            if request.is_secure():
                scheme = 'https://'
            else:
                scheme = 'http://'
            request_host = scheme + request.get_host()

            url = urlparse(self.base_url)
            base_url_host = url.scheme + '://' + url.netloc

            location = location.replace(base_url_host, request_host)
            proxy_response.headers['Location'] = location

        response = HttpProxyResponse(proxy_response)

        if self.diazo_rules and self.diazo_theme_template:
            diazo = DiazoTransformer(request, response)
            response = diazo.transform(self.diazo_rules,
                                       self.diazo_theme_template,
                                       self.html5)

        return response
