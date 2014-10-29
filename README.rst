django-revproxy
===============

.. image:: https://travis-ci.org/TracyWebTech/django-revproxy.svg
       :target: https://travis-ci.org/TracyWebTech/django-revproxy

.. image:: https://coveralls.io/repos/TracyWebTech/django-revproxy/badge.png
       :target: https://coveralls.io/r/TracyWebTech/django-revproxy 


A simple reverse proxy using Django. It allows to use Django as a 
reverse Proxy to HTTP requets. It also allows to use Django as an
authentication Proxy.


Features
---------

* Proxies GET and POST requests
* Copy all http headers sent from the client to the proxied server
* Copy all http headers sent from the proxied server to the client (except `hop-by-hop`_)
* Sets the http header REQUEST_USER if the user is logged in Django
* Handles redirects
* No external dependencies (uses only Python standard library)

.. _hop-by-hop: http://www.w3.org/Protocols/rfc2616/rfc2616-sec13.html#sec13.5.1


Install
--------

.. code-block::

    pip install django-revproxy

