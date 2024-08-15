"""
Unit tests for the MeiliSearchEngine driver in the openedx_search_api package.
"""

from django.test import TestCase

from openedx_search_api.drivers import DriverFactory


class DriverTestCase(TestCase):
    """
    Test case for MeiliSearchEngine.
    """

    def test_connection(self):
        """
        Test the connection to MeiliSearch.
        """
        client = DriverFactory.get_client(None)

        self.assertTrue(client.check_connection(), msg="Connection status")
