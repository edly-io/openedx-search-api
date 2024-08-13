"""
Module for search engine drivers and factory.
"""

from django.conf import settings
from django.utils.module_loading import import_string


class BaseDriver:
    """Base class for search engine drivers."""

    def get_user_token(self, index_search_rules=None):
        """
        Retrieve the user token based on the provided index search rules.
        
        :param index_search_rules: Optional search rules to filter the token retrieval.
        :raises NotImplementedError: If the method is not implemented in a subclass.
        """
        raise NotImplementedError("Method 'get_user_token' not implemented")

    def check_connection(self):
        """
        Check the connection to the search engine.
        
        :raises NotImplementedError: If the method is not implemented in a subclass.
        """
        raise NotImplementedError("Method 'check_connection' not implemented")

    def indexes(self):
        """
        Retrieve the list of indexes available in the search engine.
        
        :raises NotImplementedError: If the method is not implemented in a subclass.
        """
        raise NotImplementedError("Method 'indexes' not implemented")

    def index(self, index_name, index_settings):
        """
        Index the provided payload in the specified index.
        
        :param index_name: The name of the index.
        :param payload: The data to be indexed.
        :raises NotImplementedError: If the method is not implemented in a subclass.
        """
        raise NotImplementedError("Method 'index' not implemented")

    def get_search_rules(self, search_rules=None):
        """
        Retrieve the search rules based on the provided filters.
        
        :param search_rules: Optional list of string filters.
        :return: List of search rules.
        :raises NotImplementedError: If the method is not implemented in a subclass.
        """
        raise NotImplementedError("Method 'get_search_rules' not implemented")


class DriverFactory:
    """Factory class to get the search engine client."""

    def get_search_engine(self):
        """
        Return value of SEARCH_ENGINE
        :return:
        """
        return getattr(
            settings,
            'SEARCH_ENGINE',
            'openedx_search_api.drivers.meilisearch.MeiliSearchEngine'
        )

    @classmethod
    def get_client(cls, request, *args, **kwargs) -> BaseDriver:
        """
        Retrieve the search engine client based on the settings.
        
        :param request: The request object.
        :return: An instance of a subclass of BaseDriver.
        """
        search_driver = getattr(
            settings,
            'SEARCH_ENGINE',
            'openedx_search_api.drivers.meilisearch.MeiliSearchEngine'
        )
        klass = import_string(search_driver)
        return klass.get_instance(request, *args, **kwargs)
