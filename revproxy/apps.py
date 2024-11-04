from django.apps import AppConfig
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from .settings import REVPROXY_DEFAULT_SETTINGS


class RevProxyConfig(AppConfig):
    name = 'revproxy'
    verbose_name = _('Revproxy')

    def ready(self):
        super().ready()
        default_settings = {
            'REVPROXY': REVPROXY_DEFAULT_SETTINGS
        }

        if not hasattr(settings, 'REVPROXY'):
            setattr(settings, 'REVPROXY', default_settings['REVPROXY'])
        else:
            for key, value in default_settings['REVPROXY'].items():
                settings.REVPROXY.setdefault(key, value)
