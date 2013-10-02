
import re

from lxml import etree
from io import BytesIO

from django.template import loader, RequestContext

try:
    from diazo.compiler import compile_theme
except ImportError:
    has_diazo = False
else:
    has_diazo = True

doctype_re = re.compile(r"^<!DOCTYPE\s[^>]+>\s*", re.MULTILINE)


class DiazoTransformer(object):

    def __init__(self, request, response):
        self.request = request
        self.response = response

    def should_transform(self):
        """Determine if we should transform the response"""

        if not has_diazo:
            return False

        if self.request.is_ajax():
            return False

        if self.response.streaming:
            return False

        content_type = self.response.get('Content-Type')
        if not content_type or not (
            content_type.lower().startswith('text/html') or
            content_type.lower().startswith('application/xhtml+xml')
        ):
            return False

        content_encoding = self.response.get('Content-Encoding')
        if content_encoding in ('zip', 'deflate', 'compress',):
            return False

        status_code = str(self.response.status_code)
        if status_code.startswith('3') or \
                status_code == '204' or \
                status_code == '401':
            return False

        if len(self.response.content) == 0:
            return False

        return True

    def transform(self, rules, theme_template, is_html5):

        if not self.should_transform():
            return self.response

        context_instance = RequestContext(self.request, current_app=None)
        theme = loader.render_to_string(theme_template,
                                        context_instance=context_instance)
        output_xslt = compile_theme(
            rules=rules,
            theme=BytesIO(theme.encode('latin1')),
        )

        transform = etree.XSLT(output_xslt)

        content_doc = etree.fromstring(self.response.content,
                                       parser=etree.HTMLParser())

        self.response.content = transform(content_doc)

        if is_html5:
            self.set_html5_doctype()

        self.reset_headers()
        return self.response

    def reset_headers(self):
        del self.response['Content-Length']

    def set_html5_doctype(self):
        doctype = u'<!DOCTYPE html>\n'
        content, subs = doctype_re.subn(doctype, self.response.content, 1)

        if not subs:
            self.response.content = doctype + self.response.content

        self.response.content = content
