from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
)
