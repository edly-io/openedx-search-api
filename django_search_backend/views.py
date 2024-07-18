from django.http import JsonResponse
from django.views.generic import View

from django_search_backend.drivers import DriverFactory


class AuthTokenView(View):
    def get(self, request):
        client = DriverFactory.get_client(request)
        search_rules = client.get_search_rules()
        token = client.get_user_token(search_rules)

        return JsonResponse(token)
