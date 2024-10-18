from django.apps import AppConfig
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from .settings import REVPROXY_DEFAULT_SETTINGS


class RevProxyConfig(AppConfig):
    name = 'revproxy'
    verbose_name = _('Revproxy')

    def ready(self):
        super().ready()
        for setting, default_value in REVPROXY_DEFAULT_SETTINGS.items():
            setattr(
                settings,
                setting,
                getattr(settings, setting, default_value),
            )
