from revproxy.views import ProxyView


class SampleProxyView(ProxyView):
    upstream = 'https://docs.djangoproject.com'
