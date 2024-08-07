from .common import *


"""
################### Meilisearch ###################
"""
# Meilisearch URL that the python backend can use. Often points to another docker container or k8s service.
MEILISEARCH_URL = "http://localhost:7700"
# URL that browsers (end users) can use to reach Meilisearch. Should be HTTPS in production.
MEILISEARCH_PUBLIC_URL = "http://localhost:7700"
# To support multi-tenancy, you can prefix all indexes with a common key like "sandbox7-"
# and use a restricted tenant token in place of an API key, so that this Open edX instance
# can only use the index(es) that start with this prefix.
# See https://www.meilisearch.com/docs/learn/security/tenant_tokens
MEILISEARCH_INDEX_PREFIX = "meilisearch_"
MEILISEARCH_MASTER_API_KEY = "masterKey"
MEILISEARCH_API_KEY = "da7a448d-2b13-490b-8ca6-6b3e051b4201"
SEARCH_ENGINE = "openedx_search_api.drivers.meilisearch.MeiliSearchEngine"

INDEX_CONFIGURATION_CLASS = "openedx_search_api.drivers.meilisearch.BaseIndexConfiguration"
INDEXER_CLASS = "openedx_search_api.indexers.base.BaseIndexer"
INDEX_CONFIGURATIONS = {
    "user_content": {
        "options": {
            "primaryKey": "id"
        },
        "search_rules": [
            "IS_STAFF: false"
        ],
        "settings": {
            "filterableAttributes": [
                "IS_SUPERUSER",
                "USERNAME",
                "IS_STAFF"
            ]
        },
        "model_class": "auth.User",
        "fields": "__all__"
    },
    "courseware_course_structure": {
        "options": {
            "primaryKey": "item_id"
        },
        "settings": {
            "filterableAttributes": [
                "CONTENT_TYPE",
                "COURSE",
                "ORG"
            ]
        },
        "search_rules": [
            "ORG: Arbisoft"
        ],
        "content_class": "openedx.core.djangoapps.content.content_classes.courseware_search_models.CoursewareContent"
    }
}
MEILISEARCH_API_KEY_ID = "c471bd40-303b-48bc-bb80-4602baff2675"
MEILISEARCH_API_KEY="7d6b4e462ac450051d0618d277dc46051db30160bf9bc28a0dd2e7f097c9eecd"