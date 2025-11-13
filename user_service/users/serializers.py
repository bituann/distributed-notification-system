from rest_framework import serializers
from .models import User, UserPreference

class UserPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreference
        fields = ['email', 'push']

class UserSerializer(serializers.ModelSerializer):
    preferences = UserPreferenceSerializer()

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'push_token', 'preferences', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        pref_data = validated_data.pop('preferences')
        preferences = UserPreference.objects.create(**pref_data)
        user = User.objects.create(preferences=preferences, **validated_data)
        return user




