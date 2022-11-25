
Welcome to django-revproxy
==========================

.. image:: https://jazzband.co/static/img/badge.svg
    :alt: Jazzband
    :target: https://jazzband.co/

.. image:: https://img.shields.io/pypi/v/django-revproxy.svg
    :alt: PyPI version
    :target: https://pypi.org/project/django-revproxy/

.. image:: https://img.shields.io/pypi/pyversions/django-revproxy.svg
    :alt: Supported Python versions
    :target: https://pypi.org/project/django-revproxy/

.. image:: https://github.com/jazzband/django-revproxy/workflows/Test/badge.svg
   :target: https://github.com/jazzband/django-revproxy/actions
   :alt: GitHub Actions

.. image:: https://codecov.io/gh/jazzband/django-revproxy/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/jazzband/django-revproxy
   :alt: Test Coverage


A simple reverse proxy using Django. It allows to use Django as a
reverse Proxy to HTTP requests. It also allows to use Django as an
authentication Proxy.

Documentation available at http://django-revproxy.readthedocs.org/


Features
---------

* Proxies all HTTP methods: HEAD, GET, POST, PUT, DELETE, OPTIONS, TRACE, CONNECT and PATCH
* Copy all http headers sent from the client to the proxied server
* Copy all http headers sent from the proxied server to the client (except `hop-by-hop <http://www.w3.org/Protocols/rfc2616/rfc2616-sec13.html#sec13.5.1>`_)
* Basic URL rewrite
* Sets the http header REQUEST_USER if the user is logged in Django
* Sets the http headers X-Forwarded-For and X-Forwarded-Proto
* Handles redirects
* Few external dependencies
* Apply XSLT transformation in the response (requires Diazo)


Dependencies
------------

* django >= 3.0
* urllib3 >= 1.12
* diazo >= 1.0.5 (optional)
* lxml >= 3.4, < 3.5 (optional, but diazo dependency)


Install
--------

``pip install django-revproxy``

