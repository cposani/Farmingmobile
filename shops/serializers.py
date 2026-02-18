

# serializers.py

import re
from rest_framework import serializers
from .models import Product, ProductImage, SavedProduct, RecentlyViewed


# ---------------------------------------------------------
# ⭐ PRODUCT IMAGE SERIALIZER (MULTI-IMAGE SUPPORT)
# ---------------------------------------------------------
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image"]


# ---------------------------------------------------------
# ⭐ MAIN PRODUCT SERIALIZER (DETAIL + CREATE + UPDATE)
# ---------------------------------------------------------
class ProductSerializer(serializers.ModelSerializer):
    seller_username = serializers.CharField(source="seller.username", read_only=True)
    approved_by_name = serializers.CharField(source="approved_by.username", read_only=True)

    # ⭐ Multi-image field
    images = ProductImageSerializer(many=True, read_only=True)
    

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "price",
            "contact",
            "location",
            "latitude",
            "longitude",
            "images",            # ⭐ multi-image only
            "status",
            "seller",
            "seller_name",
            "seller_username",
            "approved_by",
            "approved_by_name",
            "created_at",
            "updated_at",
            "local_created_at",

        ]
        read_only_fields = [
            "id",
            "status",
            "seller",
            "seller_username",
            "approved_by",
            "approved_by_name",
            "created_at",
            "updated_at",
        ]

    # ---------------- CONTACT VALIDATION ----------------
    def validate_contact(self, value):
        import re

        raw = value.replace(" ", "")

    # Must start with + and country code (1–4 digits)
    # Must end with exactly 10 digits (national number)
        if not re.fullmatch(r"^\+[1-9]\d{7,14}$", raw):
            raise serializers.ValidationError(
                "Contact number must be in valid international format (E.164), e.g. +14155552671."
            )

        return raw

    # ---------------- CREATE PRODUCT ----------------
    def create(self, validated_data):
        user = self.context["request"].user

        # local_created_at comes from frontend
        local_time = self.context["request"].data.get("local_created_at") 
        if local_time: 
            validated_data["local_created_at"] = local_time

        validated_data["seller"] = user

        if user.is_staff:
            validated_data["status"] = Product.Status.APPROVED
            validated_data["approved_by"] = user
        else:
            validated_data["status"] = Product.Status.PENDING
            validated_data["approved_by"] = None

        return super().create(validated_data)


# ---------------------------------------------------------
# ⭐ PRODUCT LIST SERIALIZER (USED IN MARKET LIST)
# ---------------------------------------------------------
class ProductListSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ("id", "name", "price", "location", "images")


# ---------------------------------------------------------
# ⭐ MINI PRODUCT SERIALIZER (USED IN SAVED PRODUCTS)
# ---------------------------------------------------------
class ProductMiniSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "price",
            "location",
            "created_at",
            "images",      # ⭐ multi-image
        ]


# ---------------------------------------------------------
# ⭐ SAVED PRODUCT SERIALIZER
# ---------------------------------------------------------
class SavedProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = SavedProduct
        fields = ["id", "product", "created_at"]


# ---------------------------------------------------------
# ⭐ RECENTLY VIEWED SERIALIZER
# ---------------------------------------------------------
class RecentlyViewedSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)

    class Meta:
        model = RecentlyViewed
        fields = ("id", "product", "viewed_at")
