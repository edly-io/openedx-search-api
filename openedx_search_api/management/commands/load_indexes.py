import logging
import sys

from django.apps import apps
from django.core.management import BaseCommand
from django.conf import settings
from django.utils.module_loading import import_string
from rest_framework import serializers

from django_search_api.drivers import DriverFactory

log = logging.getLogger(__name__)


class Command(BaseCommand):
    def get_serializer(self, _model, _fields=None, _exclude=None):
        class BaseSerializer(serializers.ModelSerializer):
            class Meta:
                model = _model
                fields = _fields or []
                exclude = _exclude or []

        return BaseSerializer

    def handle(self, *args, **kwargs):
        client = DriverFactory.get_client(None)
        INDEXER_CLASS = getattr(self, 'INDEXER_CLASS', 'django_search_api.indexers.base.BaseIndexer')
        klass = import_string(INDEXER_CLASS)
        INDEX_CONFIGURATIONS = getattr(settings, 'INDEX_CONFIGURATIONS', {})

        for index_name, config in INDEX_CONFIGURATIONS.items():
            if 'content_class' in config:
                content_klass = import_string(config['content_class'])
                indexer = klass(index_name, None, None, client)
                documents = content_klass().fetch()
                task_info = indexer.index_documents(documents, config.get('settings', {}))
            else:
                model_klass = apps.get_model(*config['model_class'].split('.'))
                serializer_klass = self.get_serializer(model_klass, _fields=config.get('fields'))
                indexer = klass(index_name, model_klass.objects.all(), serializer_klass, client)
                task_info = indexer.index(config.get('settings', {}))
            sys.stdout.write(f"task UID: {task_info.task_uid}, index UID: {task_info.index_uid}\n")
