from rest_framework import serializers
from .models import Shop, RequestedShop

# shops/serializers.py
from rest_framework import serializers
from .models import Shop, RequestedShop
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    seller_username = serializers.CharField(source="seller.username", read_only=True)
    approved_by_name = serializers.CharField(source="approved_by.username", read_only=True)
    image = serializers.ImageField(use_url=True, required=False, allow_null=True)

    class Meta:
        model = Product
        fields = [
            "id", "name", "description", "price", "contact", "location", "image",
            "status", "seller", "seller_name", "seller_username", "approved_by", "approved_by_name",
            "created_at", "updated_at","latitude", "longitude",
        ]
        read_only_fields = [
            "id", "status", "seller", "seller_username", "approved_by", "approved_by_name",
            "created_at", "updated_at",
        ]

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["seller"] = user
        if user.is_staff:
            validated_data["status"] = Product.Status.APPROVED
            validated_data["approved_by"] = user
        else:
            validated_data["status"] = Product.Status.PENDING
            validated_data["approved_by"] = None
        return super().create(validated_data)

















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
