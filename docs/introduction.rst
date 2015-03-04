Introduction
==================

How does it work?
-----------------

At a high level, this is what happens behind the scenes in a request proxied by django-revproxy:

#. Django receives a request from the client and process it using a view that extends `revproxy.proxy.ProxyView`.

#. Revproxy will clone the client request and send it to the upstream server (set in the view).

#. If the user is authenticated in Django and `add_remote_user` attribute is set to `True` the HTTP header `REMOTE_USER` will be set with `request.user.username`.

#. After receiving the response from upstream, the view will process it to make sure all headers are set properly. Some headers like `Location` are treated as special cases.

#. The response received from the upstream server is transformed into a `django.http.HttpResponse`. For binary files `StreamingHttpResponse` is used instead to reduce memory usage.

#. If the user has setted a set of diazo rules and a theme template, a diazo/XSLT transformation will be applied on the response body.

#. Finally, the response will then be returned to the user

Visual diagram
---------------

.. image:: revproxy.jpg

