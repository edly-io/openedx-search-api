"""
Unit tests for the MeiliSearchEngine driver in the openedx_search_api package.
"""

from django.test import TestCase
from openedx_search_api.drivers.meilisearch import MeiliSearchEngine


class MeilisearchDriverTestCase(TestCase):
    """
    Test case for MeiliSearchEngine.
    """
    def test_meilisearch_connection(self):
        """
        Test the connection to MeiliSearch.
        """
        client = MeiliSearchEngine(
            None,
            "http://localhost:7800",
            "http://localhost:7800",
            "c471bd40-303b-48bc-bb80-4602baff2675",
            "7d6b4e462ac450051d0618d277dc46051db30160bf9bc28a0dd2e7f097c9eecd",
            "masterkey",
            expiry_days=7
        )

        self.assertTrue(client.check_connection(), msg="Connection status")
