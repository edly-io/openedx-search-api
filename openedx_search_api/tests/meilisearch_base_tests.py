from django.test import TestCase

from openedx_search_api.drivers.meilisearch import MeiliSearchEngine


# Create your tests here.
class MeilisearchDriverTestCase(TestCase):
    def test_meilisearch_connection(self):
        client = MeiliSearchEngine(
            None,
            "http://meilisearch:42069",
            "http://meilisearch:42069",
            "c471bd40-303b-48bc-bb80-4602baff2675",
            "7d6b4e462ac450051d0618d277dc46051db30160bf9bc28a0dd2e7f097c9eecd",
            "masterKey",
            expiry_days=7
        )

        self.assertTrue(client.check_connection(), msg="Connection status")
