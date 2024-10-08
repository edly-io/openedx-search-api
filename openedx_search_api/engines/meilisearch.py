from copy import deepcopy
from datetime import datetime
import hashlib
import json
import typing as t

import meilisearch

from django.conf import settings
from search.elastic import ElasticSearchEngine


import logging


logger = logging.getLogger(__name__)

PRIMARY_KEY_FIELD_NAME = "_pk"


class DocumentEncoder(json.JSONEncoder):
    """
    Custom encoder, useful in particular to encode datetime fields.
    Ref: https://github.com/meilisearch/meilisearch-python?tab=readme-ov-file#custom-serializer-for-documents-
    """

    def default(self, o):
        if isinstance(o, datetime):
            return str(o)
        return super().default(o)


def get_index(index_name):
    """
    Return a meilisearch index.

    Note that the index may not exist, and it will be created on first insertion.
    """
    meilisearch_client = meilisearch.Client(
        settings.MEILISEARCH_URL, api_key=settings.MEILISEARCH_API_KEY
    )
    return meilisearch_client.index(index_name)


FACETS = {"course_info": ["language", "modes", "org"]}


class MeilisearchEngine(ElasticSearchEngine):

    def __init__(self, index=None):
        super().__init__(index=index)

        # Index names are usually not configured with the right prefix, and the API key
        # is authorized to access only the indexes with the right prefix.
        self.meilisearch_index_name = (
            settings.MEILISEARCH_INDEX_PREFIX + self.index_name
        )
        self.meilisearch_index = get_index(self.meilisearch_index_name)

        # Update facets
        # TODO should we do this only at indexing time? Or search?
        facets = FACETS.get(self.index_name, [])
        if facets and self.meilisearch_index.get_filterable_attributes() != facets:
            self.meilisearch_index.update_filterable_attributes(facets)

    def index(self, sources, **kwargs):
        """
        Example request:

            sources:
                [
                    {
                        'id': 'course-v1:OpenedX+DemoX+DemoCourse',
                        'course': 'course-v1:OpenedX+DemoX+DemoCourse',
                        'content': {
                            'display_name': 'Open edX Demo Course',
                            'overview': " About This Course Welcome to... ",
                            'number': 'DemoX',
                            'short_description': 'Explore Open edX® capabilities in this...'
                        },
                        'image_url': '/asset-v1:OpenedX+DemoX+DemoCourse+type@asset+block@thumbnail_demox.jpeg',
                        'start': datetime.datetime(2020, 1, 1, 0, 0, tzinfo=<bson.tz_util.FixedOffset object at 0x750906b7a7d0>),
                        'number': 'DemoX', 'org': 'OpenedX', 'modes': ['audit'], 'language': 'en', 'catalog_visibility': 'both'
                    }
                ]
            kwargs={}

        Example request for courseware_content:

            sources=[
                {
                    "course": "course-v1:DemoX+test1+alpha",
                    "org": "DemoX",
                    "content": {"display_name": "Subsection"},
                    "content_type": "Sequence",
                    "id": "block-v1:DemoX+test1+alpha+type@sequential+block@4b20735c0dfb48899d7d1da235a18a57",
                    "start_date": datetime.datetime(2030, 1, 1, 0, 0, tzinfo=tzlocal()),
                    "content_groups": None,
                    "course_name": "test course 1",
                    "location": ["Section", "Subsection"],
                },
                {
                    "course": "course-v1:DemoX+test1+alpha",
                    "org": "DemoX",
                    "content": {"display_name": "Subsection"},
                    "content_type": "Sequence",
                    "id": "block-v1:DemoX+test1+alpha+branch@published-branch+version@6706492a2b8884312e02abe6+type@sequential+block@3f2bfd48e9aa4662b8e91b6b3400ff5d",
                    "start_date": datetime.datetime(2030, 1, 1, 0, 0, tzinfo=tzlocal()),
                    "content_groups": None,
                    "course_name": "test course 1",
                    "location": ["Section", "Subsection"],
                },
                {
                    "course": "course-v1:DemoX+test1+alpha",
                    "org": "DemoX",
                    "content": {"display_name": "Section"},
                    "content_type": "Sequence",
                    "id": "block-v1:DemoX+test1+alpha+branch@published-branch+version@6706492a2b8884312e02abe6+type@chapter+block@456ad85b17a94a139728788f5add8cd1",
                    "start_date": datetime.datetime(2030, 1, 1, 0, 0, tzinfo=tzlocal()),
                    "content_groups": None,
                    "course_name": "test course 1",
                    "location": ["Section"],
                },
            ]
            kwargs={'request_timeout': 60}
        """
        logger.info(
            "IIIIIIIIIIIIIIIIIIIIIIIIIIII [%s] Index request: sources=%s kwargs=%s",
            self.meilisearch_index_name,
            sources,
            kwargs,
        )
        # Index in meilisearch
        # Note that the primary key will only be used on creating the index.
        # Copying is necessary because we need to process the docs later with ES
        meilisearch_sources = deepcopy(sources)
        for source in meilisearch_sources:
            source[PRIMARY_KEY_FIELD_NAME] = id2pk(source["id"])
        self.meilisearch_index.add_documents(
            meilisearch_sources, serializer=DocumentEncoder, primary_key=PRIMARY_KEY_FIELD_NAME
        )

        # Index in Elasticsearch
        # TODO use the request_timeout from kwargs?
        result = super().index(sources, **kwargs)
        logger.info(
            "IIIIIIIIIIIIIIIIIIIIIIIIIIII [%s] Index result: %s",
            self.meilisearch_index_name,
            result,
        )
        return result

    def search(
        self,
        query_string=None,
        field_dictionary=None,
        filter_dictionary=None,
        exclude_dictionary=None,
        aggregation_terms=None,
        exclude_ids=None,
        use_field_match=False,
        log_search_params=False,
        **kwargs,
    ):
        """
        Example request:

            query_string=mysearchquery
            field_dictionary={}
            filter_dictionary={'enrollment_end': <search.utils.DateRange object at 0x744e242201d0>}
            exclude_dictionary={'catalog_visibility': 'none'}
            aggregation_terms={'org': {}, 'modes': {}, 'language': {}}
            exclude_ids=None
            use_field_match=False
            log_search_params=False
            kwargs={'size': 20, 'from_': 0}
        """
        logger.info(
            (
                "IIIIIIIIIIIIIIIIIIIIIIIIIIII Search request: query_string=%s "
                "field_dictionary=%s "
                "filter_dictionary=%s "
                "exclude_dictionary=%s "
                "aggregation_terms=%s "
                "exclude_ids=%s "
                "use_field_match=%s "
                "log_search_params=%s "
                "kwargs=%s"
            ),
            query_string,
            field_dictionary,
            filter_dictionary,
            exclude_dictionary,
            aggregation_terms,
            exclude_ids,
            use_field_match,
            log_search_params,
            kwargs,
        )
        es_results = super().search(
            query_string=query_string,
            field_dictionary=field_dictionary,
            filter_dictionary=filter_dictionary,
            exclude_dictionary=exclude_dictionary,
            aggregation_terms=aggregation_terms,
            exclude_ids=exclude_ids,
            use_field_match=use_field_match,
            log_search_params=log_search_params,
            **kwargs,
        )
        logger.info(
            "IIIIIIIIIIIIIIIIIIIIIIIIIIII [%s] ES search result: %s",
            self.meilisearch_index_name,
            es_results,
        )
        # return es_results

        # TODO handle the following parameters:
        # filter_dictionary={'enrollment_end': <search.utils.DateRange object at 0x73c37aaf1d90>}
        # exclude_dictionary={'catalog_visibility': 'none'}
        facets = list(aggregation_terms.keys()) if aggregation_terms else []
        meilisearch_results = self.meilisearch_index.search(
            query_string, {"showRankingScore": True, "facets": facets}
        )
        return process_results(meilisearch_results, self.index_name)


def id2pk(value: str) -> str:
    """
    Convert a document "id" field into a primary key that is compatible with Meilisearch.

    This step is necessary because the "id" is typically a course id, which includes
    colon ":" characters, which are not supported by Meilisearch. Source:
    https://www.meilisearch.com/docs/learn/getting_started/primary_key#formatting-the-document-id
    """
    return hashlib.sha1(value.encode()).hexdigest()


def process_results(results: dict[str, t.Any], index_name: str) -> dict[str, t.Any]:
    """
    Convert results produced by meilisearch into results that are compatible with the
    edx-search engine API.

    Example input:

        {
            'hits': [
                {
                    'pk': 'f381d4f1914235c9532576c0861d09b484ade634',
                    'id': 'course-v1:OpenedX+DemoX+DemoCourse',
                    ...
                    "_rankingScore": 0.865,
                },
                ...
            ],
            'query': 'demo',
            'processingTimeMs': 0,
            'limit': 20,
            'offset': 0,
            'estimatedTotalHits': 1
        }

    Example output:

        {
                'took': 13,
                'total': 1,
                'max_score': 0.4001565,
                'results': [
                    {
                        '_index': 'course_info',
                        '_type': '_doc',
                        '_id': 'course-v1:OpenedX+DemoX+DemoCourse',
                        '_ignored': ['content.overview.keyword'],
                        'data': {
                            'id': 'course-v1:OpenedX+DemoX+DemoCourse',
                            'course': 'course-v1:OpenedX+DemoX+DemoCourse',
                            'content': {
                                'display_name': 'Open edX Demo Course',
                                'overview': " About This Course Welcome to the...",
                                'number': 'DemoX',
                                'short_description': 'Explore Open edX® capabilities...'
                            },
                            'image_url': '/asset-v1:OpenedX+DemoX+DemoCourse+type@asset+block@thumbnail_demox.jpeg',
                            'start': '2020-01-01T00:00:00+00:00',
                            'number': 'DemoX',
                            'org': 'OpenedX',
                            'modes': ['audit'],
                            'language': 'en',
                            'catalog_visibility': 'both'
                        },
                        'score': 0.4001565
                    }
                ],
                'aggs': {
                    'modes': {
                        'terms': {'audit': 1},
                        'total': 1.0,
                        'other': 0
                    },
                    'org': {
                        'terms': {'OpenedX': 1}, 'total': 1.0, 'other': 0
                    },
                    'language': {'terms': {'en': 1}, 'total': 1.0, 'other': 0}
                }
            }
    """
    # Base
    processed = {
        "took": results["processingTimeMs"],
        "total": results["estimatedTotalHits"],
        "results": [],
        "aggs": {},
    }

    # Hits
    max_score = 0
    for result in results["hits"]:
        score = result.pop("_rankingScore")
        result.pop(PRIMARY_KEY_FIELD_NAME)
        max_score = max(max_score, score)
        processed_result = {
            "_id": result["id"],
            "_index": index_name,
            "_type": "_doc",
            "data": result,
        }
        processed["results"].append(processed_result)
    processed["max_score"] = max_score

    # Aggregates/Facets
    for facet_name, facet_distribution in results.get("facetDistribution", {}).items():
        total = sum(facet_distribution.values())
        processed["aggs"][facet_name] = {
            "terms": facet_distribution,
            "total": total,
            "other": 0,
        }
    return processed
