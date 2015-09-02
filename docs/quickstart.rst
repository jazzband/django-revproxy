Quickstart
=============

Installation
--------------

.. code-block:: sh

    $ pip install django-revproxy

If you want to use DiazoProxyView you will also need to install Diazo. In that case you can use the following handy shortcurt:

.. code-block:: sh

    $ pip install django-revproxy[diazo]


Configuration
--------------

After installation, you'll need to configure your application to use django-revproxy.
Start by adding revproxy to your ``settings.py`` file as follows:

.. code-block:: python

    #Add 'revproxy' to INSTALLED_APPS.
    INSTALLED_APPS = (
        # ...
        'django.contrib.auth',
        'revproxy',
        # ...
    )


Next, you'll need to create a View that extends ``revproxy.views.ProxyView`` and set the upstrem attribute:

.. code-block:: python

    from revproxy.views import ProxyView

    class TestProxyView(ProxyView):
        upstream = 'http://example.com'


And now add your view in the ``urls.py``:

.. code-block:: python

    from myapp.views import TestProxyView

    urlpatterns = patterns('', 
        url(r'^(?P<path>.*)$', TestProxyView.as_view()),
    )

Alternatively you could just use the default ProxyView as follow:

.. code-block:: python

    from revproxy.views import ProxyView

    urlpatterns = patterns('', 
        url(r'^(?P<path>.*)$', ProxyView.as_view(upstream='http://example.com/')),
    )



After starting your test server you should see the content of `http://example.com/` on `http://localhost:8000/`.

.. seealso::

        An example of a project can be found here:
        https://github.com/seocam/revproxy-test
    
        The provided test project is a simple Django project that makes
        uses of revproxy. It basically possess a view.py that extends 
        from ProxyView and sets the upstream address to 'httpbin.org'.
