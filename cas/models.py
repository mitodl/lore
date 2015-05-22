"""
Empty models required to load application configuration
"""
# HACK: This is required in order to initialize the application settings
# since models is always imported: See note on
# http://django-appconf.readthedocs.org/en/latest/
# pylint: disable=unused-import
from cas.conf import CASAppConf
