# -*- coding: utf-8 -*-

import os
import re
import sys
import mimetypes

if sys.version_info >= (3, 0, 0):  # pragma: no cover
    from urllib.parse import urljoin, urlparse, urlencode, quote
    from urllib.request import urlopen, build_opener, install_opener, Request
    from urllib.error import HTTPError
else:  # pragma: no cover
    # Fallback to Python 2.7
    from urllib import urlencode
    from urllib2 import (quote, urlopen, build_opener, install_opener,
                         HTTPError, Request)
    from urlparse import urljoin, urlparse

from django.shortcuts import redirect
from django.views.generic import View
from django.utils.decorators import classonlymethod

from .response import HttpProxyResponse
from .utils import normalize_headers, NoHTTPRedirectHandler, encode_items
from .transformer import DiazoTransformer


class ProxyView(View):
    add_remote_user = False
    diazo_theme_template = 'diazo.html'
    html5 = False
    rewrite = tuple()

    def __init__(self, *args, **kwargs):
        super(ProxyView, self).__init__(*args, **kwargs)

        self._rewrite = []
        for from_pattern, to_pattern in self.rewrite:
            from_re = re.compile(from_pattern)
            self._rewrite.append((from_re, to_pattern))

    @property
    def upstream(self):
        raise NotImplementedError('Upstream server must be set')

    @property
    def diazo_rules(self):
        child_class_file = sys.modules[self.__module__].__file__
        app_path = os.path.abspath(os.path.dirname(child_class_file))
        return os.path.join(app_path, 'diazo.xml')

    @classonlymethod
    def as_view(cls, **initkwargs):
        view = super(ProxyView, cls).as_view(**initkwargs)
        view.csrf_exempt = True
        return view

    def dispatch(self, request, path):

        # Rewrite implementation
        for from_re, to_pattern in self._rewrite:
            full_path = request.get_full_path()

            if from_re.match(full_path):
                redirect_to = from_re.sub(to_pattern, full_path)
                return redirect(redirect_to)

        request_payload = request.body
        request_headers = normalize_headers(request)

        if self.add_remote_user and request.user.is_active:
            request_headers['REMOTE_USER'] = request.user.username

        request_url = urljoin(
            self.upstream,
            quote(path.encode('utf8'))
        )

        if request.GET:
            get_data = encode_items(request.GET.lists())
            request_url += '?' + urlencode(get_data)

        proxy_request = Request(request_url, headers=request_headers)

        if request_payload:
            proxy_request.add_data(request_payload)

        opener = build_opener(NoHTTPRedirectHandler)
        install_opener(opener)

        # Make sure we'll keep the request method
        proxy_request.get_method = lambda: request.method

        try:
            proxy_response = urlopen(proxy_request)
        except HTTPError as e:
            proxy_response = e

        location = proxy_response.headers.get('Location')
        if location:
            if request.is_secure():
                scheme = 'https://'
            else:
                scheme = 'http://'
            request_host = scheme + request.get_host()

            url = urlparse(self.upstream)
            upstream_host_http = 'http://' + url.netloc
            upstream_host_https = 'https://' + url.netloc

            location = location.replace(upstream_host_http, request_host)
            location = location.replace(upstream_host_https, request_host)
            proxy_response.headers['Location'] = location

        content_type = proxy_response.headers.get('content-type')
        if not content_type:
            content_type = (mimetypes.guess_type(request.path)[0] or
                            'application/octet-stream')
            proxy_response.headers['content-type'] = content_type

        response = HttpProxyResponse(proxy_response)

        if self.diazo_rules and self.diazo_theme_template:
            diazo = DiazoTransformer(request, response)
            response = diazo.transform(self.diazo_rules,
                                       self.diazo_theme_template,
                                       self.html5)

        return response
