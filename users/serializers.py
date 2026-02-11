# serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User

from .validators import is_valid_phone

class UserSerializer(serializers.ModelSerializer):
    is_admin = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "is_admin"]

    def get_is_admin(self, obj):
        return obj.is_staff or obj.is_superuser
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile

class ProfileUpdateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name", required=False)
    last_name = serializers.CharField(source="user.last_name", required=False)
    email = serializers.EmailField(source="user.email", read_only=True)
    phone = serializers.CharField(required=False)

    class Meta:
        model = Profile
        fields = ["first_name", "last_name", "email", "phone"]

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})

        # Update User model fields
        user = instance.user
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()

        # Update Profile model fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance
    

    def validate_phone(self, value):
        if not is_valid_phone(value):
            raise serializers.ValidationError("Invalid phone number format")
        return value



class ProfileMeSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    email = serializers.EmailField(source="user.email")
    username = serializers.CharField(source="user.username")
    is_admin = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ["id", "username", "email", "first_name", "last_name", "phone", "is_admin"]

    def get_is_admin(self, obj):
        return obj.user.is_staff or obj.user.is_superuser
