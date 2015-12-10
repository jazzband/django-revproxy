
Usage
=====

============
Proxy Views
============

This document covers the views provided by ``revproxy.views`` and all it's public attributes

.. class:: revproxy.views.ProxyView

    Proxies requests to a given upstream server and returns a
    Django Response.

    **Example urls.py**::

        from revproxy.views import ProxyView

        urlpatterns = patterns('',
            url(r'^(?P<path>.*)$', ProxyView.as_view(upstream='http://example.com/')),
        )


    **Attributes**

    .. attribute:: upstream

        The URL of the proxied server. Requests will be made to this URL
        with ``path`` (extracted from ``urls.py``) appended to it.
        This attribute is mandatory.

    .. attribute:: add_remote_user

        Whether to add the ``REMOTE_USER`` to the request in case of an
        authenticated user. Defaults to ``False``.

    .. attribute:: default_content_type

        The *Content-Type* that will be added to the response in case
        the upstream server doesn't send it and if ``mimetypes.guess_type``
        is not able to guess. Defaults to ``'application/octet-stream'``.

    .. attribute:: retries

        The max number of attempts for a request. This can also be an
        instance of ``urllib3.Retry``. If set to None it will fail if
        the first attempt fails. The default value is None.

    .. attribute:: rewrite

        A list of tuples in the style ``(from, to)`` where ``from``
        must by a valid regex expression and ``to`` a valid URL. If
        ``request.get_full_path`` matches the ``from`` expression the
        request will be redirected to ``to`` with an status code
        ``302``. Matches groups can be used to pass parts from the
        ``from`` URL to the ``to`` URL using numbered groups.
        By default no rewrite is set.

        **Example**::

           class CustomProxyView(ProxyView):
               upstream = 'http://www.example.com'
               rewrite = (
                   (r'^/yellow/star/$', r'/black/hole/'),
                   (r'^/red/?$', r'http://www.mozilla.org/'),

                   # Example with numbered match groups
                   (r'^/foo/(.*)$', r'/bar\1'),
                )

    **Methods**

    .. automethod:: revproxy.views.ProxyView.get_request_headers

       Extend this method can be particularly useful to add or
       remove headers from your proxy request. See the example bellow::

          class CustomProxyView(ProxyView):
              upstream = 'http://www.example.com'

              def get_request_headers(self):
                  # Call super to get default headers
                  headers = super(CustomProxyView, self).get_request_headers()
                  # Add new header
                  headers['DNT'] = 1
                  return headers

.. class:: revproxy.views.DiazoProxyView

    In addition to ProxyView behavior this view also performs Diazo
    transformations on the response before sending it back to the
    original client. Furthermore, it's possible to pass context data
    to the view thanks to ContextMixin behavior through
    ``get_context_data()`` method.

    .. seealso::

        Diazo is an awesome tool developed by Plone Community to
        perform XSLT transformations in a simpler way. In order to
        use all Diazo power please refer to: http://diazo.org/


    **Example urls.py**::

        from revproxy.views import DiazoProxyView

        proxy_view = DiazoProxyView.as_view(
            upstream='http://example.com/',
            html5=True,
            diazo_theme_template='base.html',
        )

        urlpatterns = patterns('',
            url(r'^(?P<path>.*)$', proxy_view),
        )


    **Example base.html**

    .. code-block:: html

        <html>
            <head>...</head>
            <body>
                ...
                <div id="content"></div>
                ...
            </body>
        </html>


    **Example diazo.xml**

    .. code-block:: xml

        <rules
            xmlns="http://namespaces.plone.org/diazo"
            xmlns:css="http://namespaces.plone.org/diazo/css"
            xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

            <!-- Adds 'body' content from example.com into theme #content -->
            <before css:theme-children="#content" css:content-children="body" />
        </rules>



    **Attributes**

    .. attribute:: diazo_theme_template

        The Django template to be used as Diazo theme. If set to
        ``None`` Diazo will be disabled. By default ``diazo.html``
        will be used.

    .. attribute:: diazo_rules

        The absolute path for the diazo rules file. By default it
        will look for the file ``diazo.xml`` on the Django
        application directory. If set to ``None`` Diazo will be
        disabled.

    .. attribute:: html5

        By default Diazo changes the doctype for html5 to html4. If
        this attribute is set to ``True`` the doctype will be kept.
        This attribute only works if Diazo transformations are enabled.


    **Methods**

    .. automethod:: revproxy.views.DiazoProxyView.get_context_data

       Extend this method if you need to send context variables to the
       template before it's used in the proxied response transformation.
       This method was inherited from ContextMixin.

       .. versionadded:: 0.9.4

       See the example bellow::


          from revproxy.views import DiazoProxyView

          class CustomProxyView(DiazoProxyView):
              upstream = 'http://example.com/'
              custom_attribute = 'hello'

              def get_context_data(self, **kwargs):
                  context_data = super(CustomProxyView, self).get_context_data(**kwargs)
                  context_data.update({'foo': 'bar'})
                  return context_data


          # urls.py
          urlpatterns = patterns('',
              url(r'^(?P<path>.*)$', proxy_view),
          )


       And than the data will be available in the template as follow:

       .. code-block:: html

             <html>
               <head>...</head>
               <body>
                 ...
                 <div id="content">
                   {{ view.custom_attribute }}
                   {{ foo }}
                 </div>
                 ...
               </body>
             </html>
