import django.test

from django.utils import timezone

from openedx_search_api.engines import meilisearch as meilisearch_engine


class DocumentEncoderTests(django.test.TestCase):

    def test_document_encode_without_timezone(self):
        document = {
            "date": timezone.datetime(2024, 12, 31, 5, 0, 0),
        }
        encoder = meilisearch_engine.DocumentEncoder()
        encoded = encoder.encode(document)
        self.assertEqual('{"date": "2024-12-31 05:00:00"}', encoded)

    def test_document_encode_with_timezone(self):
        document = {
            "date": timezone.datetime(
                2024, 12, 31, 5, 0, 0, tzinfo=timezone.get_fixed_timezone(0)
            ),
        }
        encoder = meilisearch_engine.DocumentEncoder()
        encoded = encoder.encode(document)
        self.assertEqual('{"date": "2024-12-31 05:00:00+00:00"}', encoded)


class EngineTests(django.test.TestCase):

    def test_index(self):
        # TODO
        pass

    def test_search(self):
        meilisearch_results = {
            "hits": [
                {
                    "id": "id1",
                    "pk": meilisearch_engine.id2pk("id1"),
                    "title": "title 1",
                    "_rankingScore": 0.8,
                },
                {
                    "id": "id2",
                    "pk": meilisearch_engine.id2pk("id2"),
                    "title": "title 2",
                    "_rankingScore": 0.2,
                },
            ],
            "query": "demo",
            "processingTimeMs": 14,
            "limit": 20,
            "offset": 0,
            "estimatedTotalHits": 2,
        }
        processed_results = meilisearch_engine.process_results(
            meilisearch_results, "index_name"
        )
        self.assertEqual(14, processed_results["took"])
        self.assertEqual(2, processed_results["total"])
        self.assertEqual(0.8, processed_results["max_score"])

        self.assertEqual(2, len(processed_results["results"]))
        self.assertEqual(
            {
                "_id": "id1",
                "_index": "index_name",
                "_type": "_doc",
                "data": {
                    "id": "id1",
                    "title": "title 1",
                },
            },
            processed_results["results"][0],
        )
        self.assertEqual(
            {
                "_id": "id2",
                "_index": "index_name",
                "_type": "_doc",
                "data": {
                    "id": "id2",
                    "title": "title 2",
                },
            },
            processed_results["results"][1],
        )

    def test_search_with_facets(self):
        meilisearch_results = {
            "hits": [],
            "query": "",
            "processingTimeMs": 1,
            "limit": 20,
            "offset": 0,
            "estimatedTotalHits": 0,
            "facetDistribution": {
                "modes": {"audit": 1, "honor": 3},
                "facet2": {"val1": 1, "val2": 2, "val3": 3},
            },
        }
        processed_results = meilisearch_engine.process_results(
            meilisearch_results, "index_name"
        )
        aggs = processed_results["aggs"]
        self.assertEqual(
            {
                "terms": {"audit": 1, "honor": 3},
                "total": 4.0,
                "other": 0,
            },
            aggs["modes"],
        )
