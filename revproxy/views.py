# -*- coding: utf-8 -*-

import os
import re
import sys
import mimetypes
import logging

import urllib3

from django.utils.six.moves.urllib.parse import (urljoin, urlparse,
                                                 urlencode, quote_plus)

from django.shortcuts import redirect
from django.views.generic import View
from django.utils.decorators import classonlymethod

from .exceptions import InvalidUpstream
from .response import get_django_response
from .utils import normalize_headers, encode_items
from .transformer import DiazoTransformer

# Chars that don't need to be quoted. We use same than nginx:
#   https://github.com/nginx/nginx/blob/nginx-1.9/src/core/ngx_string.c
#   (Lines 1433-1449)
QUOTE_SAFE = '<.;>\(}*+|~=-$/_:^@)[{]&\'!,"`'


ERRORS_MESSAGES = {
    'upstream-no-scheme': ("Upstream URL scheme must be either "
                           "'http' or 'https' (%s).")
}


class ProxyView(View):
    """View responsable by excute proxy requests, process and return
    their responses.

    """

    add_remote_user = False
    default_content_type = 'application/octet-stream'
    retries = None
    rewrite = tuple()  # It will be overrided by a tuple inside tuple.

    def __init__(self, *args, **kwargs):
        super(ProxyView, self).__init__(*args, **kwargs)

        self._rewrite = []
        # Take all elements inside tuple, and insert into _rewrite
        for from_pattern, to_pattern in self.rewrite:
            from_re = re.compile(from_pattern)
            self._rewrite.append((from_re, to_pattern))
        self.http = urllib3.PoolManager()
        self.log = logging.getLogger('revproxy.view')
        self.log.info("ProxyView created")

    @property
    def upstream(self):
        raise NotImplementedError('Upstream server must be set')

    def get_upstream(self, path):
        upstream = self.upstream

        if not getattr(self, '_parsed_url', None):
            self._parsed_url = urlparse(upstream)

        if self._parsed_url.scheme not in ('http', 'https'):
            raise InvalidUpstream(ERRORS_MESSAGES['upstream-no-scheme'] %
                                  upstream)

        if path and upstream[-1] != '/':
            upstream += '/'

        return upstream

    @classonlymethod
    def as_view(cls, **initkwargs):
        view = super(ProxyView, cls).as_view(**initkwargs)
        view.csrf_exempt = True
        return view

    def _format_path_to_redirect(self, request):
        full_path = request.get_full_path()
        self.log.debug("Dispatch full path: %s", full_path)
        for from_re, to_pattern in self._rewrite:
            if from_re.match(full_path):
                redirect_to = from_re.sub(to_pattern, full_path)
                self.log.debug("Redirect to: %s", redirect_to)
                return redirect_to

    def get_proxy_request_headers(self, request):
        """Get normalized headers for the upstream

        Gets all headers from the original request and normalizes them.
        Normalization occurs by replacing 'HTTP\_' to '' and '_' to '-'

        The header REMOTE_USER is set to the current user
        if this view's add_remote_user property is True

        .. versionadded:: 0.9.1

        :param request:  The original HTTPRequest instance
        :returns:  Normalized headers for the upstream
        """
        request_headers = normalize_headers(request)

        if self.add_remote_user and request.user.is_active:
            request_headers['REMOTE_USER'] = request.user.username
            self.log.info("REMOTE_USER set")

        return request_headers

    def _created_proxy_response(self, request, path):
        request_payload = request.body

        request_headers = self.get_proxy_request_headers(request)
        self.log.debug("Request headers: %s", request_headers)

        request_url = urljoin(
            self.get_upstream(path),
            quote_plus(path.encode('utf8'), QUOTE_SAFE)
        )
        self.log.debug("Request URL: %s", request_url)

        if request.GET:
            get_data = encode_items(request.GET.lists())
            request_url += '?' + urlencode(get_data)
            self.log.debug("Request URL: %s", request_url)

        try:
            proxy_response = self.http.urlopen(request.method,
                                               request_url,
                                               redirect=False,
                                               retries=self.retries,
                                               headers=request_headers,
                                               body=request_payload,
                                               decode_content=False,
                                               preload_content=False)
            self.log.debug("Proxy response header: %s",
                           proxy_response.getheaders())
        except urllib3.exceptions.HTTPError as error:
            self.log.exception(error)
            raise

        return proxy_response

    def _replace_host_on_redirect_location(self, request, proxy_response):
        location = proxy_response.headers.get('Location')
        if location:
            if request.is_secure():
                scheme = 'https://'
            else:
                scheme = 'http://'
            request_host = scheme + request.get_host()

            upstream_host_http = 'http://' + self._parsed_url.netloc
            upstream_host_https = 'https://' + self._parsed_url.netloc

            location = location.replace(upstream_host_http, request_host)
            location = location.replace(upstream_host_https, request_host)
            proxy_response.headers['Location'] = location
            self.log.debug("Proxy response LOCATION: %s",
                           proxy_response.headers['Location'])

    def _set_content_type(self, request, proxy_response):
        content_type = proxy_response.headers.get('Content-Type')
        if not content_type:
            content_type = (mimetypes.guess_type(request.path)[0] or
                            self.default_content_type)
            proxy_response.headers['Content-Type'] = content_type
            self.log.debug("Proxy response CONTENT-TYPE: %s",
                           proxy_response.headers['Content-Type'])

    def dispatch(self, request, path):
        redirect_to = self._format_path_to_redirect(request)
        if redirect_to:
            return redirect(redirect_to)

        proxy_response = self._created_proxy_response(request, path)

        self._replace_host_on_redirect_location(request, proxy_response)
        self._set_content_type(request, proxy_response)

        response = get_django_response(proxy_response)

        self.log.debug("RESPONSE RETURNED: %s", response)
        return response


class DiazoProxyView(ProxyView):

    diazo_theme_template = 'diazo.html'
    html5 = False

    @property
    def diazo_rules(self):
        child_class_file = sys.modules[self.__module__].__file__
        app_path = os.path.abspath(os.path.dirname(child_class_file))
        diazo_path = os.path.join(app_path, 'diazo.xml')

        self.log.debug("diazo_rules: %s", diazo_path)
        return diazo_path

    def dispatch(self, request, path):
        response = super(DiazoProxyView, self).dispatch(request, path)

        diazo = DiazoTransformer(request, response)
        response = diazo.transform(self.diazo_rules, self.diazo_theme_template,
                                   self.html5)

        return response
