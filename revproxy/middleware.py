
from lxml import etree
from io import BytesIO

from django.template import loader, RequestContext

from diazo.compiler import compile_theme


class DiazoProxyMiddleware(object):
    def process_response(self, request, response):
        if response.streaming:
            return response

        if not response.get('Content-Type').startswith('text/html'):
            return response

        rules = getattr(request, 'diazo_rules', None)
        theme_template = getattr(request, 'diazo_theme_template', None)
        if not rules or not theme_template:
            return response

        context_instance = RequestContext(request, current_app=None)
        theme = loader.render_to_string(request.diazo_theme_template,
                                        context_instance=context_instance)

        output_xslt = compile_theme(
            rules=rules,
            theme=BytesIO(theme.encode('utf-8')),
        )

        transform = etree.XSLT(output_xslt)

        content_doc = etree.fromstring(response.content)
        response.content = transform(content_doc)

        return response
