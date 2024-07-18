from django.conf import settings
from django.utils.module_loading import import_string


class DriverFactory:
    @classmethod
    def get_client(cls, request, *args, **kwargs):
        search_driver = getattr(settings, 'SEARCH_ENGINE', 'search.meilisearch.MeiliSearchEngine')
        klass = import_string(search_driver)
        return klass.get_instance(request, *args, **kwargs)
