import uuid
from django.db import models

class UserPreference(models.Model):
    email = models.BooleanField(default=True)
    push = models.BooleanField(default=True)

class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    push_token = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=128)
    preferences = models.OneToOneField(UserPreference, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
