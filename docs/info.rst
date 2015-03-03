Basic Informations
==================

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

* django >= 1.6
* urllib3 >= 1.10.1
* six >= 1.9.0
* diazo >= 1.0.1 (optional)


Install
--------

``pip install django-revproxy``

