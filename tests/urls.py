from django.conf.urls import patterns, url

urlpatterns = patterns('',  # noqa
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', name='login'),
)
