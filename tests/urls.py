from django.conf.urls import url
try:
    from django.contrib.auth.views import login
except ImportError:
    # Django 2.2 moved this
    from django.contrib.auth import login

urlpatterns = [
    url(r'^accounts/login/$', login, name='login'),
]
