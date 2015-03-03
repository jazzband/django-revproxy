Quickstart
=============

Installation
--------------

Follow theses instructions to set up with basic install of revproxy

.. code-block:: sh

    $ pip install django-revproxy


Configuration
--------------

After installation, you'll need to configure your application to use django-revproxy.
Start by making the following changes to your ``settings.py`` file:

.. code-block:: python

    #Add 'revproxy' to INSTALLED_APPS.
    INSTALLED_APPS = (
        # ...
        'django.contrib.auth',
        'revproxy',
        # ...
    )


Next, it is necessary to create a View that extends revproxy ProxyView and sets the revproxy variable that you will use:

.. code-block:: python

    from revproxy,views import ProxyView

    class TestProxyView(ProxyView):

        upstream = '....'
        diazo_rules = '....'
        diazo_theme_templates = '.....'
        html5 = '.....'
        add_remote_user = '.....'


This variable main objectives are:

    1. upstream: A String that holds the address for the upstream server that the client wants to access
    2. diazo_rules: A set of diazo rules that will guide the xlst transformation
    3. diazo_theme_template: The path to a file that contains the template on which the diazo transformation will placed upon. Therefore this file
                             will provide the template for the new content of the response.
    4. html5: A variable that states if the response content will be a html5
    5. add_remote_user: Used to set a remote user header if the upstream server needs authentication.

Once the view is implemented and the variables required by the user are setted, the file urls.py needs to changed:

.. code-block:: python

    from myapp.views import TestProxyView

    urlpatterns = patterns('', 
        url(r'^(?P<path>.*)$', TestProxyView.as_view()),
    )

This is the necessary steps to use revproxy on your project. A test project can be found on the link:


https://github.com/seocam/revproxy-test


Test project
---------------

The provided test project is a simple django app that makes uses of revproxy. It basically possess a view.py that extends from ProxyView and sets the upstream address to
'httpbin.org'.


Before running the revproxy-test, run the following command on the projec root:

.. code-block:: sh

    $ pip install -r requirements.txt

This command will install revproxy and its other dependencies for running revproxy-test.

After that, in order to run the test, go into the src/ directory and run the following command:

.. code-block:: sh
    
    $python manage.py runserver


Once you enter into your localhost, it will be seen that revproxy will be able to redirect the localhost the upstream address and its response will possess the actual localhost location, 
and not the upstream one. 
