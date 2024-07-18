from django.http import JsonResponse
from django.views.generic import View

from search.drivers import DriverFactory


class AuthTokenView(View):
    def get(self, request):
        client = DriverFactory.get_client(request)
        token = client.get_user_token({
            'meilisearch_courseware_content': {}
        })

        return JsonResponse(token)
