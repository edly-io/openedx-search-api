"""
Management command to load indexes into MeiliSearch.
"""

import logging
import sys

from django.apps import apps
from django.core.management import BaseCommand
from django.conf import settings
from django.utils.module_loading import import_string
from rest_framework import serializers

from django_search_api.drivers import DriverFactory  # pylint: disable=import-error

log = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Command to load indexes into MeiliSearch.
    """

    def get_serializer(self, model_class, list_fields=None, list_exclude=None):
        """
        Create a serializer class for the given model.

        :param model_class: The Django model class.
        :param list_fields: Fields to include in the serializer.
        :param list_exclude: Fields to exclude from the serializer.
        :return: A serializer class for the model.
        """

        class BaseSerializer(serializers.ModelSerializer):
            """
            Serializer class for the model.
            """

            # pylint: disable=too-few-public-methods
            class Meta:
                """
                Meta class for the serializer.
                """
                model = model_class
                fields = list_fields or []
                exclude = list_exclude or []

        return BaseSerializer

    def handle(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Handle the management command execution.

        :param args: Positional arguments.
        :param kwargs: Keyword arguments.
        """
        client = DriverFactory.get_client(None)
        indexer_class = getattr(
            self, 'INDEXER_CLASS', 'django_search_api.indexers.base.BaseIndexer'
        )
        klass = import_string(indexer_class)
        index_configurations = getattr(settings, 'INDEX_CONFIGURATIONS', {})

        for index_name, config in index_configurations.items():
            if 'content_class' in config:
                content_klass = import_string(config['content_class'])
                indexer = klass(index_name, None, None, client)
                documents = content_klass().fetch()
                task_info = indexer.index_documents(
                    documents, config.get('settings', {})
                )
            else:
                model_klass = apps.get_model(*config['model_class'].split('.'))
                serializer_klass = self.get_serializer(
                    model_klass, list_fields=config.get('fields')
                )
                indexer = klass(
                    index_name, model_klass.objects.all(), serializer_klass, client
                )
                task_info = indexer.index(config.get('settings', {}))
            sys.stdout.write(
                f"task UID: {task_info.task_uid}, index UID: {task_info.index_uid}\n"
            )
