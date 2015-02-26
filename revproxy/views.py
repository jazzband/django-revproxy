# -*- coding: utf-8 -*-

import os
import re
import sys
import mimetypes
import logging

import urllib3

from six.moves.urllib.parse import urljoin, urlparse, urlencode, quote

from django.shortcuts import redirect
from django.views.generic import View
from django.utils.decorators import classonlymethod

from .response import get_django_response
from .utils import normalize_headers, encode_items
from .transformer import DiazoTransformer


class ProxyView(View):
    #: Variable to add remote_user to request
    add_remote_user = False
    #: Variable that represents the name of file containing
    #: the diazo theme template
    diazo_theme_template = 'diazo.html'
    #: Variable verify if html5 will be used
    html5 = False
    #: Variable used to store a tuple of string , first is a route to the
    #: application login and the second one replaces and redirects the first
    #: path
    rewrite = tuple()

    def __init__(self, *args, **kwargs):
        super(ProxyView, self).__init__(*args, **kwargs)

        self._rewrite = []
        for from_pattern, to_pattern in self.rewrite:
            from_re = re.compile(from_pattern)
            self._rewrite.append((from_re, to_pattern))

        self.http = urllib3.PoolManager()
        self.log = logging.getLogger('revproxy')

    @property
    def upstream(self):
        """This method is not implemanted on the base class """
        raise NotImplementedError('Upstream server must be set')

    @property
    def diazo_rules(self):
        """Method to create a path to the file containing the diazo rules

        :returns: Path of diazo rules file
        """
        child_class_file = sys.modules[self.__module__].__file__
        app_path = os.path.abspath(os.path.dirname(child_class_file))
        return os.path.join(app_path, 'diazo.xml')

    @classonlymethod
    def as_view(cls, **initkwargs):
        """This method return a callable View that take a request and returns a
        response, but the View will have a Cross-site request forgery verified

        :returns: A callable view
        """
        view = super(ProxyView, cls).as_view(**initkwargs)
        view.csrf_exempt = True
        return view

    def __format_path_to_redirect(self, request):
        """This method evaluate if the path request must be redirected and
        return the full path to redirect or  a blank string

        :param    request: The paramater is a HttpRequest
        :returns: A string containing the full path to be redirect
                  or an empty string
        """
        redirect_to = ""
        full_path = request.get_full_path()
        for from_re, to_pattern in self._rewrite:
            if from_re.match(full_path):
                redirect_to = from_re.sub(to_pattern, full_path)
                return redirect_to
        return redirect_to

    def __created_proxy_response(self, request, path):
        """This method is reponsible for creating a new request based on
        the parameters of the original request. The new request will possess
        formatted headers.

        :param request: The paramater is a HttpRequest
        :param path:    The parameter is the current path from client
        :returns:       Return an urllib3.response.HTTPResponse from
                        the created request
        """
        proxy_response = None
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

        try:
            proxy_response = self.http.urlopen(request.method,
                                               request_url,
                                               redirect=False,
                                               headers=request_headers,
                                               body=request_payload,
                                               decode_content=False,
                                               preload_content=False)
        except urllib3.exceptions.HTTPError as error:
            self.log.exception(error)
            raise

        return proxy_response

    def __set_location_from_original_request(self, request, proxy_response):
        """This method change the location header from proxy_response to the
        location header of request

        :param request:         The original request received from
                                the dispatch method
        :param proxy_response:  The response created by
                                the method __created_proxy_response
        """
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

    def __set_content_type_from_original_request(self, request,
                                                 proxy_response):
        """This method change the Content-Type header from proxy_response
        to the location header of request

        :param request:         The original request received from
                                the dispatch method
        :param proxy_response:  The response created by
                                the method __created_proxy_response
        """
        content_type = proxy_response.headers.get('Content-Type')
        if not content_type:
            content_type = (mimetypes.guess_type(request.path)[0] or
                            'application/octet-stream')
            proxy_response.headers['Content-Type'] = content_type

    def dispatch(self, request, path):
        """This method is used to create a http response from the
        proxied server and return to the client.It must be said
        that the http response from the proxied server will be modified
        based on the headers and content-type from the client request and
        also on the specified diazo rules and template

        :param  request:    The paramater is a HttpRequest
        :param  path:       The parameter is the current path from client
        :returns:           Return is a django.http.HttpResponse based on both
                            diazo rules and template
        """

        redirect_to = self.__format_path_to_redirect(request)
        if(redirect_to):
            return redirect(redirect_to)

        try:
            proxy_response = self.__created_proxy_response(request, path)
        except urllib3.exceptions.HTTPError:
            raise

        self.__set_location_from_original_request(request, proxy_response)

        self.__set_content_type_from_original_request(request, proxy_response)

        response = get_django_response(proxy_response)

        if self.diazo_rules and self.diazo_theme_template:
            diazo = DiazoTransformer(request, response)
            response = diazo.transform(self.diazo_rules,
                                       self.diazo_theme_template,
                                       self.html5)

        return response
