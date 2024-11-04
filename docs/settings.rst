Settings
========

Our configurations are all namespaced under the ``REVPROXY`` settings.

For example:

.. code-block:: python

    REVPROXY = {
        'QUOTE_SPACES_AS_PLUS': True,
    }


List of available settings
--------------------------

QUOTE_SPACES_AS_PLUS
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default: ``True``

Indicates whether spaces should be replaced by %20 or + when parsing a URL.
