
Usage
=====

==========
Proxy View
==========

.. module:: revproxy.views.ProxyView
      :synopsis: View used for Proxy requests

This document covers the ``revproxy.views.ProxyView`` and all it's public attributes

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

    .. attribute:: diazo_theme_template

        The Django template to be used as Diazo theme. If set to
        ``None`` Diazo will be disabled. By default ``diazo.html``
        will be used.

    .. attribute:: diazo_rules

        The diazo rules file to be used. By default it will look for
        the file ``diazo.xml`` on the Django application directory.
        If set to ``None`` Diazo will be disabled.

    .. attribute:: html5

        By default Diazo changes the doctype for html5 to html4. If
        this attribute is set to ``True`` the doctype will be kept.
        This attribute only works if Diazo transformations are enabled.
