"""
Views for the openedx_search_api application.
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.generic import View

from .drivers import DriverFactory


class AuthTokenView(LoginRequiredMixin, View):
    """
    View to handle the generation and return of an authentication token.
    """
    def get(self, request):
        """
        Handle GET requests to generate a user token with search rules.

        :param request: The HTTP request object.
        :return: JsonResponse containing the token.
        """
        client = DriverFactory.get_client(request)
        search_rules = client.get_search_rules()
        token = client.get_user_token(search_rules)

        return JsonResponse(token)
