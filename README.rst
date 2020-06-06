
Welcome to django-revproxy
==========================

.. image:: https://travis-ci.org/TracyWebTech/django-revproxy.svg?branch=master
       :target: https://travis-ci.org/TracyWebTech/django-revproxy

.. image:: https://coveralls.io/repos/TracyWebTech/django-revproxy/badge.svg
       :target: https://coveralls.io/r/TracyWebTech/django-revproxy?branch=master

.. image:: https://api.codeclimate.com/v1/badges/1a7c55e48fa7310d5590/maintainability
      :target: https://codeclimate.com/github/TracyWebTech/django-revproxy/maintainability
      :alt: Maintainability

.. image:: https://pepy.tech/badge/django-revproxy
      :target: https://pepy.tech/project/django-revproxy
      :alt: Downloads

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
* Handles redirects
* Few external dependencies
* Apply XSLT transformation in the response (requires Diazo)


Dependencies
------------

* django >= 1.8
* urllib3 >= 1.12
* diazo >= 1.0.5 (optional)
* lxml >= 3.4, < 3.5 (optional, but diazo dependency)


Install
--------

``pip install django-revproxy``

