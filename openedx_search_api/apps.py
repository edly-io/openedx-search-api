"""
App configurations
"""
from django.apps import AppConfig


class SearchConfig(AppConfig):
    """
    App configuration class
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'openedx_search_api'

    plugin_app = {
        'url_config': {
            'lms.djangoapp': {
                'namespace': 'grades_api',
                'regex': '^api/search/',
                'relative_path': 'urls',
            }
        },
        # 'settings_config': {
        #     'lms.djangoapp': {
        #         'production': {'relative_path': 'settings.production'},
        #     },
        #     'cms.djangoapp': {
        #         'production': {'relative_path': 'settings.production'},
        #     },
        # }
    }
