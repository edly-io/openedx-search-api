from datetime import datetime, timezone, timedelta
from typing import Optional, Mapping, Any, List, Dict

from django.conf import settings
from django.utils.module_loading import import_string
from meilisearch import Client as MeilisearchClient, errors
from meilisearch.errors import MeilisearchError
from meilisearch.index import Index
from meilisearch.models.key import Key

from . import BaseDriver


class BaseIndexConfiguration(BaseDriver):
    def __init__(self, request):
        self.request = request
        self._INDEX_CONFIGURATIONS = getattr(
            settings,
            'INDEX_CONFIGURATIONS',
            {}
        )

    @property
    def indexes(self):
        return self._INDEX_CONFIGURATIONS.keys()

    def get_search_rules(self, search_rules=None):
        if search_rules is None:
            search_rules = []
        rules = {}
        for index, config in self._INDEX_CONFIGURATIONS.items():
            rules[index] = {'filter': ' AND '.join(config.get('search_rules', []) + search_rules)}
        return rules


class MeiliSearchEngine(BaseDriver):
    SEARCH_ENGINE = 'meilisearch'

    def __init__(self, request, meilisearch_url, meilisearch_public_url, meilisearch_api_id, meilisearch_api_key,
                 meilisearch_master_api_key, expiry_days=7):
        self._index = None
        self.API_KEY_ID = meilisearch_api_id
        self.API_KEY = meilisearch_api_key
        self.URL = meilisearch_url
        self.PUBLIC_URL = meilisearch_public_url
        self._MEILI_API_KEY_UID = None
        self.token_expires_at = datetime.now(tz=timezone.utc) + timedelta(days=expiry_days)
        self.request = request
        self.client: MeilisearchClient = MeilisearchClient(self.URL, meilisearch_master_api_key)

    def check_connection(self):
        try:
            self.client.health()
            return True
        except MeilisearchError as err:
            self.client = None
            raise ConnectionError("Unable to connect to Meilisearch") from err

    def create_key(self) -> Key:
        return self.client.create_key(
            {'actions': ['*'], 'indexes': ['*'],
             'expiresAt': str(self.token_expires_at.isoformat().replace("+00:00", "Z")), 'description': ''})

    def _get_meili_api_key_uid(self):
        """
        Helper method to get the UID of the API key we're using for Meilisearch
        """
        if self._MEILI_API_KEY_UID is None:
            self._MEILI_API_KEY_UID = self.client.get_key(self.API_KEY_ID).uid
        return self._MEILI_API_KEY_UID

    def get_user_token(self, index_search_rules=None):
        # Note: the following is just generating a JWT. It doesn't actually make an API call to Meilisearch.
        restricted_api_key = self.client.generate_tenant_token(
            api_key_uid=self._get_meili_api_key_uid(),
            search_rules=index_search_rules or {},
            expires_at=self.token_expires_at,
            api_key=self.API_KEY
        )

        return {
            "url": self.PUBLIC_URL,
            "token": restricted_api_key,
            "token_type": "Bearer",
            "expires_at": self.token_expires_at,
            "search_engine": self.SEARCH_ENGINE,
            "index_search_rules": index_search_rules
        }

    def indexes(self, parameters: Optional[Mapping[str, Any]] = None) -> Dict[str, List[Index]]:
        return self.client.get_indexes(parameters=parameters)

    @classmethod
    def get_instance(cls, request):
        meilisearch_url = getattr(settings, 'MEILISEARCH_URL')
        meilisearch_public_url = getattr(settings, 'MEILISEARCH_PUBLIC_URL')
        meilisearch_api_key_id = getattr(settings, 'MEILISEARCH_API_KEY_ID')
        meilisearch_api_key = getattr(settings, 'MEILISEARCH_API_KEY')
        meilisearch_master_api_key = getattr(settings, 'MEILISEARCH_MASTER_API_KEY')
        return MeiliSearchEngine(
            request,
            meilisearch_url,
            meilisearch_public_url,
            meilisearch_api_key_id,
            meilisearch_api_key,
            meilisearch_master_api_key
        )

    def _get_search_rules_class(self, *args, **kwargs) -> BaseIndexConfiguration:
        index_config = getattr(
            settings,
            'INDEX_CONFIGURATION_CLASS',
            'django_search_api.drivers.meilisearch.BaseIndexConfiguration'
        )
        klass = import_string(index_config)
        return klass(self.request, *args, **kwargs)

    def get_search_rules(self, search_rules=None):
        if search_rules is None:
            search_rules = []
        rules_instance = self._get_search_rules_class()
        return rules_instance.get_search_rules(search_rules=search_rules)

    def index(self, index_name, _settings=None, options=None):
        self._index = self.client.index(index_name)
        try:
            self._index.fetch_info()
        except errors.MeilisearchApiError:
            self.client.create_index(index_name, options or {})
            self._index.update_settings(_settings or {})
        return self._index
