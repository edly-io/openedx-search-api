"""
Management command to load indexes into MeiliSearch.
"""

import logging
import sys

from django.apps import apps
from django.conf import settings
from django.core.management import BaseCommand
from django.utils.module_loading import import_string
from rest_framework import serializers

from openedx_search_api.drivers import DriverFactory

log = logging.getLogger(__name__)


def string_to_dict(s: str):
    """
    This function takes formatted string and return object of dict.
    :param s: string formatted filters
    :return:
    """
    if not s:  # Check if the string is empty
        return {}
    return dict(item.split('=') for item in s.split(','))


class Command(BaseCommand):
    """
    Command to load indexes into MeiliSearch.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            '-i',
            '--index',
            nargs='+',
            default=[],
            help='Set specific index names e.g. "courseware_course_structure user_content"'
        )
        parser.add_argument(
            '-f',
            '--filters',
            default='',
            type=str,
            help='Set filter to select specific dataset e.g. "pk:1"'
        )

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

    def handle(self, *args, **kwargs):  # pylint: disable=unused-argument,too-many-locals
        """
        Handle the management command execution.

        :param args: Positional arguments.
        :param kwargs: Keyword arguments.
        """
        index_list = kwargs.get('index', [])
        filters = string_to_dict(kwargs.get('filters', ''))
        client = DriverFactory.get_client(None)
        indexer_class = getattr(
            self, 'INDEXER_CLASS', 'openedx_search_api.indexers.base.BaseIndexer'
        )
        klass = import_string(indexer_class)
        index_configurations = getattr(settings, 'INDEX_CONFIGURATIONS', {})

        for index_name, config in index_configurations.items():
            if index_list and index_name not in index_list:
                continue
            if 'content_class' in config:
                content_klass = import_string(config['content_class'])
                indexer = klass(index_name, None, None, client)
                documents = content_klass().fetch()
                task_info = indexer.index_documents(
                    documents, config.get('settings', {})
                )
                sys.stdout.write(
                    f"task UID: {task_info.task_uid}, index UID: {task_info.index_uid}\n"
                )
            else:
                model_klass = apps.get_model(*config['model_class'].split('.'))
                serializer_klass = self.get_serializer(
                    model_klass, list_fields=config.get('fields')
                )
                queryset = model_klass.objects.filter(**filters)
                if queryset.exists():
                    indexer = klass(
                        index_name, queryset, serializer_klass, client
                    )
                    task_info = indexer.index(config.get('settings', {}))
                    sys.stdout.write(
                        f"task UID: {task_info.task_uid}, index UID: {task_info.index_uid}\n"
                    )
                else:
                    sys.stdout.write(
                        f"there is not data to update in index:{index_name}\n"
                    )
