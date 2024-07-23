from django.db.models import QuerySet
from rest_framework.serializers import Serializer

from ..drivers.meilisearch import MeiliSearchEngine


class BaseIndexer:
    def __init__(self, index_name, queryset: QuerySet, serializer_class, client: MeiliSearchEngine):
        self.queryset = queryset
        self.serializer_class = serializer_class
        self.client = client
        self.index_name = index_name

    def index(self, settings=None, options=None):
        serializer: Serializer = self.serializer_class(self.queryset, many=True)
        index = self.client.index(self.index_name, settings=settings, options=options)
        return index.add_documents(serializer.data)
