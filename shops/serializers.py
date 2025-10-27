from rest_framework import serializers
from .models import Shop, RequestedShop

# shops/serializers.py
from rest_framework import serializers
from .models import Shop, RequestedShop

class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = [
            "id", "name", "address", "city", "latitude", "longitude",
            "contact_number", "products",
            "monday_hours", "tuesday_hours", "wednesday_hours",
            "thursday_hours", "friday_hours", "saturday_hours", "sunday_hours",
        ]


class RequestedShopSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = RequestedShop
        fields = [
            "id", "user", "name", "address", "city",
            "contact_number", "products", "status", "created_at"
        ]
        read_only_fields = ["status", "user", "created_at"]
