"""
Module for MeiliSearch Engine integration with Django.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Mapping, Optional

from django.conf import settings
from django.utils.module_loading import import_string
from meilisearch import Client as MeilisearchClient
from meilisearch import errors
from meilisearch.errors import MeilisearchError
from meilisearch.index import Index
from meilisearch.models.key import Key

from . import BaseDriver
from ..models import SearchEngineToken, SearchApiKeyModel


class BaseIndexConfiguration:
    """
    Base configuration for indexing in MeiliSearch.
    """

    def __init__(self, request):
        self.request = request
        self.index_configurations = getattr(
            settings,
            'INDEX_CONFIGURATIONS',
            {}
        )

    @property
    def indexes(self):
        """
        Returns list of indexes
        :return:
        """
        return self.index_configurations.keys()

    def get_search_rules(self, search_rules=None):
        """
        Return queries based on search_rules
        :param search_rules:
        :return:
        """
        if search_rules is None:
            search_rules = []
        rules = {}
        for index, config in self.index_configurations.items():
            rules[index] = {'filter': ' AND '.join(config.get('search_rules', []) + search_rules)}
        return rules


class MeiliSearchEngine(BaseDriver):  # pylint disable=too-many-instance-attributes
    """
    MeiliSearch Engine driver.
    """
    SEARCH_ENGINE = 'meilisearch'

    def __init__(
            self,
            request,
            meilisearch_url,
            meilisearch_public_url,
            meilisearch_master_api_key,
            expiry_days=7
    ):  # pylint: disable=too-many-arguments
        self._index = None
        self.url = meilisearch_url
        self.public_url = meilisearch_public_url
        self.token_expires_at = datetime.now(tz=timezone.utc) + timedelta(days=expiry_days)
        self.request = request
        self.client: MeilisearchClient = MeilisearchClient(self.url, meilisearch_master_api_key)

    def check_connection(self):
        """
        Check the connection to MeiliSearch.
        """
        try:
            self.client.health()
            return True
        except MeilisearchError as err:
            self.client = None
            raise ConnectionError("Unable to connect to Meilisearch") from err

    def create_key(self) -> Key:
        """
        Create an API key in MeiliSearch.
        """
        return self.client.create_key(
            {
                'actions': ['*'],
                'indexes': ['*'],
                'expiresAt': str(self.token_expires_at.isoformat().replace("+00:00", "Z")),
                'description': ''
            }
        )

    def get_api_key(self):
        """
        Returns api key pair [api_key_uid, api_key]
        :return:
        """
        api_key_model_object = SearchApiKeyModel.get_active_api_key(self.request.user)
        if not api_key_model_object:
            api_key = self.create_key()
            SearchApiKeyModel.objects.update_or_create(
                user=self.request.user,
                defaults={
                    'uid': api_key.uid,
                    'name': api_key.name,
                    'actions': api_key.actions,
                    'indexes': api_key.indexes,
                    'expires_at': api_key.expires_at,
                    'key': api_key.key,
                    'created_at': api_key.created_at,
                    'updated_at': api_key.updated_at,
                }
            )
            return api_key.uid, api_key.key
        return api_key_model_object.uid, api_key_model_object.key

    def get_user_token(self, index_search_rules=None):
        """
        Generate a user token for MeiliSearch.
        """
        response = {
            "url": self.public_url,
            "token_type": "Bearer",
            "expires_at": self.token_expires_at,
            "search_engine": self.SEARCH_ENGINE,
            "index_search_rules": index_search_rules
        }
        token = SearchEngineToken.get_active_token(self.request.user)
        if not token:
            api_key_uid, key = self.get_api_key()
            restricted_api_key = self.client.generate_tenant_token(
                api_key_uid=api_key_uid,
                search_rules=index_search_rules or {},
                expires_at=self.token_expires_at,
                api_key=key
            )
            response.update(token=restricted_api_key)
            SearchEngineToken.objects.update_or_create(
                defaults={
                    'token': restricted_api_key,
                    'token_type': "Bearer",
                    'expires_at': self.token_expires_at,
                    'search_engine': self.SEARCH_ENGINE,
                    'index_search_rules': index_search_rules or {},
                },
                user=self.request.user
            )
        else:
            response.update(
                expires_at=token.expires_at,
                token=token.token,
                index_search_rules=token.index_search_rules
            )

        return response

    def indexes(self, parameters: Optional[Mapping[str, Any]] = None) -> Dict[str, List[Index]]:
        """
        Get indexes from MeiliSearch.
        """
        return self.client.get_indexes(parameters=parameters)

    @classmethod
    def get_instance(cls, request):
        """
        Get an instance of MeiliSearchEngine.
        """
        meilisearch_url = getattr(settings, 'MEILISEARCH_URL')
        meilisearch_public_url = getattr(settings, 'MEILISEARCH_PUBLIC_URL')
        meilisearch_master_api_key = getattr(settings, 'MEILISEARCH_MASTER_API_KEY')
        return MeiliSearchEngine(
            request,
            meilisearch_url,
            meilisearch_public_url,
            meilisearch_master_api_key
        )

    def _get_search_rules_class(self, *args, **kwargs) -> BaseIndexConfiguration:
        """
        Get the class for search rules configuration.
        """
        index_config = getattr(
            settings,
            'INDEX_CONFIGURATION_CLASS',
            'openedx_search_api.drivers.meilisearch.BaseIndexConfiguration'
        )
        klass = import_string(index_config)
        return klass(self.request, *args, **kwargs)

    def get_search_rules(self, search_rules=None):
        """
        Get search rules for MeiliSearch.
        """
        if search_rules is None:
            search_rules = []
        rules_instance = self._get_search_rules_class()
        return rules_instance.get_search_rules(search_rules=search_rules)

    def index(self, index_name, index_settings=None, options=None):
        """
        Get or create an index in MeiliSearch.
        """
        self._index = self.client.index(index_name)
        try:
            self._index.fetch_info()
        except errors.MeilisearchApiError:
            self.client.create_index(index_name, options or {})
            self._index.update_settings(index_settings or {})
        return self._index
