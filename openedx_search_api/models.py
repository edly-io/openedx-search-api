"""
Define you models here
"""
from datetime import datetime

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class SearchEngineToken(models.Model):
    """
    It is to store user specific token in database
    """
    token = models.TextField()
    token_type = models.CharField(max_length=255)
    expires_at = models.DateTimeField()
    search_engine = models.CharField(max_length=255)
    index_search_rules = models.JSONField()
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    objects = models.Manager()

    @classmethod
    def get_active_token(cls, user):
        """
        Returns active token key object
        :param user:
        :return:
        """
        return cls.objects.filter(user_id=user.id, expires_at__gt=datetime.now()).first()


class SearchApiKeyModel(models.Model):
    """
    It is to store user specific api key in database
    """
    uid = models.CharField(max_length=255)
    name = models.CharField(max_length=255, blank=True, null=True)
    actions = models.JSONField()
    indexes = models.JSONField()
    expires_at = models.DateTimeField()
    key = models.CharField(max_length=500)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    objects = models.Manager()

    @classmethod
    def get_active_api_key(cls, user):
        """
        Returns active api key object
        :param user:
        :return:
        """
        return cls.objects.filter(user_id=user.id, expires_at__gt=datetime.now()).first()
