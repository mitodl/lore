"""CAS application configuration"""
from appconf import AppConf
from django.contrib.admin import autodiscover
from django.conf import settings
from django.core.urlresolvers import reverse


class CASAppConf(AppConf):
    """Configuration class for a configurable CAS authentication system"""

    ENABLED = False
    SERVER_URL = 'http://example.com'

    def configure_enabled(self, value):
        """Setup everything else if we are enabled."""
        # self required for API to work
        # pylint: disable=no-self-use,unused-argument
        if getattr(settings, 'CAS_ENABLED', False) is True:
            settings.CAS_ENABLED = True
            settings.INSTALLED_APPS += ('django_cas_ng',)
            settings.MIDDLEWARE_CLASSES += (
                'django_cas_ng.middleware.CASMiddleware',
            )
            settings.AUTHENTICATION_BACKENDS += (
                'django_cas_ng.backends.CASBackend',
            )
            # HACK: Rerun admin autodiscover since we have redone
            # applications now and we are past normal admin discovery
            autodiscover()
            settings.LOGIN_URL = reverse('cas_login')
            settings.LOGOUT_URL = reverse('cas_logout')
            settings.LOGIN_REDIRECT_URL = '/'
            return True
        else:
            return False
