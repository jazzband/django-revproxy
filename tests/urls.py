from django.urls import path

from django.contrib.auth import login

urlpatterns = [
    path('accounts/login/', login, name='login'),
]
