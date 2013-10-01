
from lxml import etree
from io import BytesIO

from django.template import loader, RequestContext

from diazo.compiler import compile_theme


class DiazoTransformer(object):

    def __init__(self, request, response):
        self.request = request
        self.response = response

    def should_transform(self):
        """Determine if we should transform the response"""

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

    def transform(self, rules, theme_template):

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

        self.reset_headers()
        return self.response

    def reset_headers(self):
        del self.response['Content-Length']
