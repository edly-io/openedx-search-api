from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.generic import View

from .drivers import DriverFactory


class AuthTokenView(LoginRequiredMixin, View):
    def get(self, request):
        client = DriverFactory.get_client(request)
        search_rules = client.get_search_rules()
        token = client.get_user_token(search_rules)

        return JsonResponse(token)
