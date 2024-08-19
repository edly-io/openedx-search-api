"""
Unit tests for the MeiliSearchEngine driver in the openedx_search_api package.
"""
import json

from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory

from openedx_search_api.drivers import DriverFactory
from openedx_search_api.views import AuthTokenView


class DriverTestCase(TestCase):
    """
    Test case for MeiliSearchEngine.
    """

    def setUp(self):
        self.request_factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass'
        )

    def test_connection(self):
        """
        Test the connection to MeiliSearch.
        """
        client = DriverFactory.get_client(None)

        self.assertTrue(client.check_connection(), msg="Connection status")

    def test_create_api_key(self):
        """
        Create api key test
        """
        request = self.request_factory.get('/token')
        request.user = self.user
        client = DriverFactory.get_client(request)
        uid, key = client.get_api_key()
        self.assertIsNotNone(uid)
        self.assertIsNotNone(key)

    def test_token_view(self):
        """
        Tests create token view
        """
        request = self.request_factory.get('/token')
        request.user = self.user
        response = AuthTokenView().get(request)
        payload = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn('index_search_rules', payload)
        self.assertIn('token', payload)
        self.assertIn('expires_at', payload)
        self.assertIn('search_engine', payload)
