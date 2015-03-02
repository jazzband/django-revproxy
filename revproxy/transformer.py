
import re

from io import BytesIO

import logging

from six import string_types
from django.template import loader, RequestContext

try:
    from diazo.compiler import compile_theme
except ImportError:
    HAS_DIAZO = False
else:
    HAS_DIAZO = True
    from lxml import etree

from .utils import get_charset, is_html_content_type

doctype_re = re.compile(br"^<!DOCTYPE\s[^>]+>\s*", re.MULTILINE)

DIAZO_OFF_REQUEST_HEADER = 'HTTP_X_DIAZO_OFF'
DIAZO_OFF_RESPONSE_HEADER = 'X-Diazo-Off'


def asbool(value):
    is_string = isinstance(value, string_types)

    if is_string:
        value = value.strip().lower()
        if value in ('true', 'yes', 'on', 'y', 't', '1',):
            return True
        elif value in ('false', 'no', 'off', 'n', 'f', '0'):
            return False
        else:
            raise ValueError("String is not true/false: %r" % value)
    else:
        return bool(value)


class DiazoTransformer(object):

    def __init__(self, request, response):
        self.request = request
        self.response = response
        self.log = logging.getLogger('revproxy.transformer')
        self.log.info("DiazoTransformer created")

    def should_transform(self):
        """
        Determine if we should transform the response
        """

        if not HAS_DIAZO:
            self.log.info("HAS_DIAZO: false")
            return False

        if asbool(self.request.META.get(DIAZO_OFF_REQUEST_HEADER)):
            self.log.info("DIAZO_OFF_REQUEST_HEADER in request.META: off")
            return False

        if asbool(self.response.get(DIAZO_OFF_RESPONSE_HEADER)):
            self.log.info("DIAZO_OFF_RESPONSE_HEADER in response.get: off")
            return False

        if self.request.is_ajax():
            self.log.info("Request is AJAX")
            return False

        if self.response.streaming:
            self.log.info("Response has streaming")
            return False

        content_type = self.response.get('Content-Type')
        if not is_html_content_type(content_type):
            self.log.info("Content-type: false")
            return False

        content_encoding = self.response.get('Content-Encoding')
        if content_encoding in ('zip', 'compress'):
            self.log.info("Content encode is %s", content_encoding)
            return False

        status_code = str(self.response.status_code)
        if status_code.startswith('3') or \
                status_code == '204' or \
                status_code == '401':
            self.log.info("Status code: %s", status_code)
            return False

        if len(self.response.content) == 0:
            self.log.info("Response Content is EMPTY")
            return False

        self.log.info("Transform")
        return True

    def transform(self, rules, theme_template, is_html5):

        if not self.should_transform():
            self.log.info("Don't need to be transformed")
            return self.response

        context_instance = RequestContext(self.request)
        theme = loader.render_to_string(theme_template,
                                        context_instance=context_instance)
        output_xslt = compile_theme(
            rules=rules,
            theme=BytesIO(theme.encode('latin1')),
        )

        transform = etree.XSLT(output_xslt)
        self.log.debug("Transform: %s", transform)

        charset = get_charset(self.response.get('Content-Type'))
        content_doc = etree.fromstring(self.response.content.decode(charset),
                                       parser=etree.HTMLParser())

        self.response.content = transform(content_doc)

        if is_html5:
            self.set_html5_doctype()

        self.reset_headers()

        self.log.debug("Response transformer: %s", self.response)
        return self.response

    def reset_headers(self):
        self.log.info("Reset header")
        del self.response['Content-Length']

    def set_html5_doctype(self):
        doctype = b'<!DOCTYPE html>\n'
        content = doctype_re.subn(doctype, self.response.content, 1)[0]
        self.response.content = content
