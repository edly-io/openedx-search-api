"""
Settings configuration for the search API plugin.
"""

def plugin_settings(settings):
    """
    Configure settings for the search API plugin.

    Args:
        settings: The settings object to configure.
    """
    settings.INDEX_CONFIGURATION_CLASS = (
        "openedx_search_api.drivers.meilisearch.BaseIndexConfiguration"
    )
    settings.INDEXER_CLASS = (
        "openedx_search_api.indexers.base.BaseIndexer"
    )
    settings.INDEX_CONFIGURATIONS = {
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
                    "content_type",
                    "course",
                    "org"
                ]
            },
            "content_class": (
                "openedx.core.djangoapps.content.content_classes."
                "courseware_search_models.CoursewareContent"
            )
        }
    }
