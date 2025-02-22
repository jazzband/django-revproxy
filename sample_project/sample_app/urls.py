from django.urls import re_path

from .views import SampleProxyView

urlpatterns = [
    re_path(r'(?P<path>.*)', SampleProxyView.as_view()),
]
