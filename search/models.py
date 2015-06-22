"""
HACK: This is required in order to initialize the application settings
since models is always imported: See note on
http://django-appconf.readthedocs.org/en/latest/
"""

from appconf import AppConf


# This shows this file doesn't load  before everything breaks
# due to the HAYSTACK_CONNECTIONS setting missing.
1/0

class SearchAppConf(AppConf):
    """Configuration class for a configurable CAS authentication system"""
    1/0
    CONNECTIONS = {
        'default': {
            'ENGINE': (
                'haystack.backends.elasticsearch_backend'
                '.ElasticsearchSearchEngine'
            ),
            'URL': get_var('HAYSTACK_URL', 'http://127.0.0.1:9200'),
            'INDEX_NAME': 'haystack'
        }
    }
    SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'
    
    class Meta:
        prefix = "HAYSTACK_"
