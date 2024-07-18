from datetime import datetime, timezone, timedelta
from typing import Optional, Mapping, Any, List, Dict

from django.conf import settings
from meilisearch import Client as MeilisearchClient
from meilisearch.errors import MeilisearchError
from meilisearch.index import Index
from meilisearch.models.key import Key


class MeiliSearchEngine:

    def __init__(self, request, meilisearch_url, meilisearch_public_url, meilisearch_api_key,
                 meilisearch_master_api_key, expiry_days=7):
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
            self._MEILI_API_KEY_UID = self.client.get_key(self.API_KEY).uid
        return self._MEILI_API_KEY_UID

    def get_user_token(self, index_search_rules=dict()):
        # Note: the following is just generating a JWT. It doesn't actually make an API call to Meilisearch.
        restricted_api_key = self.client.generate_tenant_token(
            api_key_uid=self._get_meili_api_key_uid(),
            search_rules=index_search_rules,
            expires_at=self.token_expires_at,
        )

        return {
            "url": self.PUBLIC_URL,
            "token": restricted_api_key,
            "token_type": "Bearer",
            "expires_at": self.token_expires_at
        }

    def indexes(self, parameters: Optional[Mapping[str, Any]] = None) -> Dict[str, List[Index]]:
        return self.client.get_indexes(parameters=parameters)

    @classmethod
    def get_instance(cls, request):
        MEILISEARCH_URL = getattr(settings, 'MEILISEARCH_URL')
        MEILISEARCH_PUBLIC_URL = getattr(settings, 'MEILISEARCH_PUBLIC_URL')
        MEILISEARCH_API_KEY = getattr(settings, 'MEILISEARCH_API_KEY')
        MEILISEARCH_MASTER_API_KEY = getattr(settings, 'MEILISEARCH_MASTER_API_KEY')
        return MeiliSearchEngine(
            request,
            MEILISEARCH_URL,
            MEILISEARCH_PUBLIC_URL,
            MEILISEARCH_API_KEY,
            MEILISEARCH_MASTER_API_KEY
        )
