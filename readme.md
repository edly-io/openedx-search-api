# Django Search Integration

Welcome to the **Django Search** project! This implementation supports multiple search engines and is configured to use
**Meilisearch** by default.

## Installation

To get started, install the package using the following command:

```sh
pip install git+https://github.com/qasimgulzar/django-search.git
```

## Implementation Checklist

1. [x] Generate token based of search rules
2. [x] Configurable data indexing commands
3. [ ] API endpoint for token

## Configuration

Configure your Django settings to integrate with Meilisearch:

```python
################### Meilisearch Configuration ###################

# The URL for Meilisearch that the backend can use. Typically, this points to another Docker container or a Kubernetes service.
MEILISEARCH_URL = "http://localhost:7700"

# The public URL that end users (browsers) can use to access Meilisearch. Ensure this is HTTPS in a production environment.
MEILISEARCH_PUBLIC_URL = "http://localhost:7700"

# For multi-tenancy, you can prefix all indexes with a common key, like "sandbox7-", and use a restricted tenant token 
# instead of an API key. This way, the Open edX instance can only access indexes starting with this prefix.
# Learn more at: https://www.meilisearch.com/docs/learn/security/tenant_tokens
MEILISEARCH_INDEX_PREFIX = "meilisearch_"

# Meilisearch API keys for accessing the search service
MEILISEARCH_MASTER_API_KEY = "masterKey"
MEILISEARCH_API_KEY = "da7a448d-2b13-490b-8ca6-6b3e051b4201"

# Specify the search engine driver to use Meilisearch
SEARCH_ENGINE = "django_search_backend.drivers.meilisearch.MeiliSearchEngine"
INDEX_CONFIGURATION_CLASS = "django_search_backend.drivers.meilisearch.BaseIndexConfiguration"
INDEXER_CLASS = "django_search_backend.indexers.base.BaseIndexer"

# Index name for courseware information
COURSEWARE_INFO_INDEX_NAME = 'course_info'
```

## Rules Based Tokens

1. Set below mentioned configurations to set token wide search rules on index.

```python
INDEX_CONFIGURATION_CLASS = "django_search_backend.drivers.meilisearch.BaseIndexConfiguration"
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
        "content_class": "openedx.core.djangoapps.content.content_classes.courseware_search_models.CoursewareContent"
    }
}
```

2. After updating settings you can use below snippet to generate personalised token.

```python
    from django_search_backend.drivers import DriverFactory

client = DriverFactory.get_client(request)
search_rules = client.get_search_rules()
token = client.get_user_token(search_rules)
```