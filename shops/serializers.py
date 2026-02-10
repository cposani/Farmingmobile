# # shops/serializers.py
# import re
# from rest_framework import serializers
# from .models import Product, ProductImage

# class ProductImageSerializer(serializers.ModelSerializer): 
#     class Meta: 
#         model = ProductImage
#         fields = ["id", "image"]

# class ProductSerializer(serializers.ModelSerializer):
#     seller_username = serializers.CharField(source="seller.username", read_only=True)
#     approved_by_name = serializers.CharField(source="approved_by.username", read_only=True)
#     image = serializers.ImageField(use_url=True, required=False, allow_null=True)
#     images = ProductImageSerializer(many=True, read_only=True)

#     class Meta:
#         model = Product
#         fields = [
#             "id",
#             "name",
#             "description",
#             "price",
#             "contact",
#             "location",
#             "images",
#             "status",
#             "seller",
#             "seller_name",
#             "seller_username",
#             "approved_by",
#             "approved_by_name",
#             "created_at",
#             "updated_at",
#             "latitude",
#             "longitude",
#         ]
#         read_only_fields = [
#             "id",
#             "status",
#             "seller",
#             "seller_username",
#             "approved_by",
#             "approved_by_name",
#             "created_at",
#             "updated_at",
#         ]

#     def validate_contact(self, value):
#         # Normalize: remove spaces
#         raw = value.replace(" ", "")

#         if not raw.startswith("+91"):
#             raise serializers.ValidationError("Phone number must start with + (91).")

#         if not re.fullmatch(r"\+91\d{10}", raw):
#             raise serializers.ValidationError("Phone must be +91 followed by exactly 10 digits.")

#         # Country-specific rule for India
#         if raw.startswith("+91") and len(raw) != 13:
#             raise serializers.ValidationError("Indian numbers must be +91 followed by 10 digits.")

#         return raw  # store normalized

#     def create(self, validated_data):
#         user = self.context["request"].user
#         validated_data["seller"] = user
#         if user.is_staff:
#             validated_data["status"] = Product.Status.APPROVED
#             validated_data["approved_by"] = user
#         else:
#             validated_data["status"] = Product.Status.PENDING
#             validated_data["approved_by"] = None
#         return super().create(validated_data)
# # serializers.py

# from rest_framework import serializers
# from .models import SavedProduct, Product  # adjust imports

# class ProductMiniSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Product
#         fields = [
#             "id",
#             "name",
#             "description",
#             "price",
#             "image",
#             "location",
#             "created_at",
#             # add other fields you need
#         ]

# class SavedProductSerializer(serializers.ModelSerializer):
#     product = ProductSerializer(read_only=True)

#     class Meta:
#         model = SavedProduct
#         fields = ["id", "product", "created_at"]


# from .models import Product, RecentlyViewed
# class ProductListSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Product
#         fields = ("id", "name", "price", "image", "location")  # adjust as needed


# class RecentlyViewedSerializer(serializers.ModelSerializer):
#     product = ProductListSerializer(read_only=True)

#     class Meta:
#         model = RecentlyViewed
#         fields = ("id", "product", "viewed_at")

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
        raw = value.replace(" ", "")

        if not raw.startswith("+91"):
            raise serializers.ValidationError("Phone number must start with +91.")

        if not re.fullmatch(r"\+91\d{10}", raw):
            raise serializers.ValidationError("Phone must be +91 followed by exactly 10 digits.")

        return raw

    # ---------------- CREATE PRODUCT ----------------
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
