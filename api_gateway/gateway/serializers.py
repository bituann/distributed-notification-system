from rest_framework import serializers
from enum import Enum

class NotificationType(str, Enum):
    email = "email"
    push = "push"

class UserDataSerializer(serializers.Serializer):
    name = serializers.CharField()
    link = serializers.URLField()
    meta = serializers.DictField(required=False)

class NotificationRequestSerializer(serializers.Serializer):
    notification_type = serializers.ChoiceField(choices=[(tag.value, tag.value) for tag in NotificationType])
    user_id = serializers.UUIDField()
    template_code = serializers.CharField()
    variables = UserDataSerializer()
    request_id = serializers.CharField()
    priority = serializers.IntegerField()
    metadata = serializers.DictField(required=False)
