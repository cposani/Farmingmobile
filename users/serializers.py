# serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
class UserSerializer(serializers.ModelSerializer):
    is_admin = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "is_admin"]

    def get_is_admin(self, obj):
        return obj.is_staff or obj.is_superuser
