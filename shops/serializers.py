# shops/serializers.py
import re
from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    seller_username = serializers.CharField(source="seller.username", read_only=True)
    approved_by_name = serializers.CharField(source="approved_by.username", read_only=True)
    image = serializers.ImageField(use_url=True, required=False, allow_null=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "price",
            "contact",
            "location",
            "image",
            "status",
            "seller",
            "seller_name",
            "seller_username",
            "approved_by",
            "approved_by_name",
            "created_at",
            "updated_at",
            "latitude",
            "longitude",
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

    def validate_contact(self, value):
        # Normalize: remove spaces
        raw = value.replace(" ", "")

        if not raw.startswith("+"):
            raise serializers.ValidationError("Phone number must start with + (country code).")

        if not re.fullmatch(r"\+\d{7,13}", raw):
            raise serializers.ValidationError("Invalid phone number format. Use + and 7–13 digits.")

        # Country-specific rule for India
        if raw.startswith("+91") and len(raw) != 13:
            raise serializers.ValidationError("Indian numbers must be +91 followed by 10 digits.")

        return raw  # store normalized

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
