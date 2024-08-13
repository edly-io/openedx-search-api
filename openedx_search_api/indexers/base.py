"""
Base indexer module for MeiliSearch integration with Django.
"""

from django.db.models import QuerySet
from rest_framework.serializers import Serializer

from ..drivers.meilisearch import MeiliSearchEngine


class BaseIndexer:
    """
    Base class for indexing documents in MeiliSearch.
    """

    def __init__(self, index_name: str, queryset: QuerySet,
                 serializer_class: type(Serializer), client: MeiliSearchEngine):
        """
        Initialize the BaseIndexer.

        :param index_name: Name of the index in MeiliSearch.
        :param queryset: Django QuerySet to be indexed.
        :param serializer_class: Serializer class to serialize the queryset data.
        :param client: Instance of MeiliSearchEngine.
        """
        self.queryset = queryset
        self.serializer_class = serializer_class
        self.client = client
        self.index_name = index_name

    def index(self, settings=None, options=None):
        """
        Index the queryset data in MeiliSearch.

        :param settings: Optional settings for the index.
        :param options: Optional options for the index creation.
        :return: Response from MeiliSearch add_documents API.
        """
        serializer: Serializer = self.serializer_class(self.queryset, many=True)
        index = self.client.index(self.index_name, index_settings=settings, options=options)
        return index.add_documents(serializer.data)

    def index_documents(self, documents: list, settings=None, options=None):
        """
        Index a list of documents in MeiliSearch.

        :param documents: List of documents to be indexed.
        :param settings: Optional settings for the index.
        :param options: Optional options for the index creation.
        :return: Response from MeiliSearch add_documents API.
        """
        index = self.client.index(self.index_name, index_settings=settings, options=options)
        return index.add_documents(documents)
