# -*- coding: utf-8 -*-

import os
import re
import sys
import mimetypes
import logging

import urllib3

try:
    from django.utils.six.moves.urllib.parse import (
        urlparse, urlencode, quote_plus)
except ImportError:
    # Django 3 has no six
    from urllib.parse import urlparse, urlencode, quote_plus

from django.shortcuts import redirect
from django.views.generic import View
from django.utils.decorators import classonlymethod
from django.views.generic.base import ContextMixin

from .exceptions import InvalidUpstream
from .response import get_django_response
from .transformer import DiazoTransformer
from .utils import normalize_request_headers, encode_items

# Chars that don't need to be quoted. We use same than nginx:
#   https://github.com/nginx/nginx/blob/nginx-1.9/src/core/ngx_string.c
#   (Lines 1433-1449)
QUOTE_SAFE = r'<.;>\(}*+|~=-$/_:^@)[{]&\'!,"`'


ERRORS_MESSAGES = {
    'upstream-no-scheme': ("Upstream URL scheme must be either "
                           "'http' or 'https' (%s).")
}

HTTP_POOLS = urllib3.PoolManager(maxsize=os.environ.get('ES_REVPROXY_POOL_SIZE',100))


class ProxyView(View):
    """View responsable by excute proxy requests, process and return
    their responses.

    """
    _upstream = None

    add_remote_user = False
    default_content_type = 'application/octet-stream'
    retries = None
    rewrite = tuple()  # It will be overrided by a tuple inside tuple.
    strict_cookies = False

    def __init__(self, *args, **kwargs):
        super(ProxyView, self).__init__(*args, **kwargs)

        self._rewrite = []
        # Take all elements inside tuple, and insert into _rewrite
        for from_pattern, to_pattern in self.rewrite:
            from_re = re.compile(from_pattern)
            self._rewrite.append((from_re, to_pattern))
        self.http = HTTP_POOLS
        self.log = logging.getLogger('revproxy.view')
        self.log.info("ProxyView created")

    @property
    def upstream(self):
        if not self._upstream:
            raise NotImplementedError('Upstream server must be set')
        return self._upstream

    @upstream.setter
    def upstream(self, value):
        self._upstream = value

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
        Normalization occurs by removing the prefix ``HTTP_`` and
        replacing and ``_`` by ``-``. Example: ``HTTP_ACCEPT_ENCODING``
        becames ``Accept-Encoding``.

        .. versionadded:: 0.9.1

        :param request:  The original HTTPRequest instance
        :returns:  Normalized headers for the upstream
        """
        return normalize_request_headers(request)

    def get_request_headers(self):
        """Return request headers that will be sent to upstream.

        The header REMOTE_USER is set to the current user
        if AuthenticationMiddleware is enabled and
        the view's add_remote_user property is True.

        .. versionadded:: 0.9.8

        """
        request_headers = self.get_proxy_request_headers(self.request)

        if (self.add_remote_user and hasattr(self.request, 'user')
                and self.request.user.is_active):
            request_headers['REMOTE_USER'] = self.request.user.get_username()
            self.log.info("REMOTE_USER set")

        return request_headers

    def get_quoted_path(self, path):
        """Return quoted path to be used in proxied request"""
        return quote_plus(path.encode('utf8'), QUOTE_SAFE)

    def get_encoded_query_params(self):
        """Return encoded query params to be used in proxied request"""
        get_data = encode_items(self.request.GET.lists())
        return urlencode(get_data)

    def _created_proxy_response(self, request, path):
        request_payload = request.body

        self.log.debug("Request headers: %s", self.request_headers)

        path = self.get_quoted_path(path)

        request_url = self.get_upstream(path) + path
        self.log.debug("Request URL: %s", request_url)

        if request.GET:
            request_url += '?' + self.get_encoded_query_params()
            self.log.debug("Request URL: %s", request_url)

        try:
            proxy_response = self.http.urlopen(request.method,
                                               request_url,
                                               redirect=False,
                                               retries=self.retries,
                                               headers=self.request_headers,
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
        self.request_headers = self.get_request_headers()

        redirect_to = self._format_path_to_redirect(request)
        if redirect_to:
            return redirect(redirect_to)

        proxy_response = self._created_proxy_response(request, path)

        self._replace_host_on_redirect_location(request, proxy_response)
        self._set_content_type(request, proxy_response)

        response = get_django_response(proxy_response,
                                       strict_cookies=self.strict_cookies)

        self.log.debug("RESPONSE RETURNED: %s", response)
        return response


class DiazoProxyView(ProxyView, ContextMixin):
    _diazo_rules = None
    diazo_theme_template = 'diazo.html'
    html5 = False

    @property
    def diazo_rules(self):
        if not self._diazo_rules:
            child_class_file = sys.modules[self.__module__].__file__
            app_path = os.path.abspath(os.path.dirname(child_class_file))
            diazo_path = os.path.join(app_path, 'diazo.xml')

            self.log.debug("diazo_rules: %s", diazo_path)
            self._diazo_rules = diazo_path
        return self._diazo_rules

    @diazo_rules.setter
    def diazo_rules(self, value):
        self._diazo_rules = value

    def dispatch(self, request, path):
        response = super(DiazoProxyView, self).dispatch(request, path)

        context_data = self.get_context_data()
        diazo = DiazoTransformer(request, response)
        response = diazo.transform(self.diazo_rules, self.diazo_theme_template,
                                   self.html5, context_data)

        return response
