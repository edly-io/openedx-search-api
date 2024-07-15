from django.conf import settings
from django.http import JsonResponse
from django.views.generic import View

from search.drivers.meilisearch import MeiliSearchEngine

# Create your views here.

MEILISEARCH_URL = getattr(settings, 'MEILISEARCH_URL')
MEILISEARCH_PUBLIC_URL = getattr(settings, 'MEILISEARCH_PUBLIC_URL')
MEILISEARCH_API_KEY = getattr(settings, 'MEILISEARCH_API_KEY')
MEILISEARCH_MASTER_API_KEY = getattr(settings, 'MEILISEARCH_MASTER_API_KEY')


class ListIndexView(View):
    def get(self, request):
        client = MeiliSearchEngine(request, MEILISEARCH_URL, MEILISEARCH_PUBLIC_URL, MEILISEARCH_API_KEY,
                                   MEILISEARCH_MASTER_API_KEY)
        token = client.get_user_token({
            'meilisearch_courseware_content': {}
        })

        return JsonResponse(token)
