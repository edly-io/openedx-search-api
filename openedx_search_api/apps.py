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
