from django.db import models
from datetime import datetime
# from farms.utils import geocode_address
from django.utils import timezone
from django.contrib.auth.models import User

# market/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator

User = get_user_model()

# class Product(models.Model):
#     class Status(models.TextChoices):
#         PENDING = "PENDING", "Pending"
#         APPROVED = "APPROVED", "Approved"
#         REJECTED = "REJECTED", "Rejected"

#     name = models.CharField(max_length=120)
#     description = models.TextField()
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     location = models.CharField(max_length=120)
#     latitude = models.FloatField(null=True, blank=True)
#     longitude = models.FloatField(null=True, blank=True)

#     contact = models.CharField(
#         max_length=20,
#         validators=[
#             RegexValidator(
#                 regex=r'^\+91\d{10}$',
#                 message="Contact number must be in the format +91 followed by 10 digits.",
#                 code="invalid_contact"
#             )
#         ],
#         help_text="Enter a valid phone number: +91 followed by 10 digits.",
#     )

#     # ✅ Image upload
#     # image = models.ImageField(upload_to="products/", null=True, blank=True)
#     seller_name=models.CharField(max_length=50,blank=True,null=True)
#     seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="products")
#     status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
#     approved_by = models.ForeignKey(
#         User, null=True, blank=True, on_delete=models.SET_NULL, related_name="approved_products"
#     )

#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"{self.name} ({self.status})"
    

# class ProductImage(models.Model): 
#     product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE) 
#     image = models.ImageField(upload_to="products/") 
#     def __str__(self): 
#         return f"Image for {self.product.name}"

# from django.conf import settings
# from django.db import models
# from .models import Product  # adjust import if Product is elsewhere

# class SavedProduct(models.Model):
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="saved_products"
#     )
#     product = models.ForeignKey(
#         Product,
#         on_delete=models.CASCADE,
#         related_name="saved_by_users"
#     )
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = ("user", "product")
#         ordering = ["-created_at"]

#     def __str__(self):
#         return f"{self.user} saved {self.product}"


# class RecentlyViewed(models.Model):
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="recently_viewed",
#     )
#     product = models.ForeignKey(
#         Product,
#         on_delete=models.CASCADE,
#         related_name="viewed_by",
#     )
#     viewed_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         unique_together = ("user", "product")
#         ordering = ("-viewed_at",)

#     def __str__(self):
#         return f"{self.user} viewed {self.product} at {self.viewed_at}"





from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.conf import settings
import requests

User = get_user_model()


# ---------------------------------------------------------
# ⭐ Helper: LocationIQ Geocoding (Free tier, No card)
# ---------------------------------------------------------
def geocode_address(address):
    """
    Uses LocationIQ forward geocoding to convert address → (lat, lon).

    - Works for street addresses, ZIP codes, cities, etc.
    - Uses your LOCATIONIQ_API_KEY from settings.
    """
    print("DEBUG: LOCATIONIQ KEY =", settings.LOCATIONIQ_API_KEY)
    try:
        api_key = settings.LOCATIONIQ_API_KEY
        if not api_key:
            print("LocationIQ API key missing in settings.LOCATIONIQ_API_KEY")
            return None, None

        url = "https://us1.locationiq.com/v1/search"
        params = {
            "key": api_key,
            "q": address,
            "format": "json",
            "limit": 1,
        }

        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        if isinstance(data, list) and len(data) > 0:
            first = data[0]
            lat = float(first.get("lat"))
            lon = float(first.get("lon"))
            return lat, lon

    except Exception as e:
        print("LocationIQ geocoding error:", e)

    return None, None


# ---------------------------------------------------------
# ⭐ PRODUCT MODEL
# ---------------------------------------------------------
class Product(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    name = models.CharField(max_length=120)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    # User-entered address
    location = models.CharField(max_length=120)

    # Auto-filled by frontend OR backend
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    contact = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+91\d{10}$',
                message="Contact number must be in the format +91 followed by 10 digits.",
                code="invalid_contact"
            )
        ],
        help_text="Enter a valid phone number: +91 followed by 10 digits.",
    )

    seller_name = models.CharField(max_length=50, blank=True, null=True)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="products")

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    approved_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="approved_products"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ---------------------------------------------------------
    # ⭐ AUTO‑GEOCODE ON SAVE (Safe, Non‑Breaking)
    # ---------------------------------------------------------
    def save(self, *args, **kwargs):
        """
        Auto-fill latitude & longitude when:
        - location exists AND
        - latitude/longitude are missing
        """
        if self.location and (not self.latitude or not self.longitude):
            lat, lon = geocode_address(self.location)
            if lat and lon:
                self.latitude = lat
                self.longitude = lon

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.status})"


# ---------------------------------------------------------
# ⭐ PRODUCT IMAGE MODEL
# ---------------------------------------------------------
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="products/")

    def __str__(self):
        return f"Image for {self.product.name}"


# ---------------------------------------------------------
# ⭐ SAVED PRODUCT MODEL
# ---------------------------------------------------------
class SavedProduct(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="saved_products"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="saved_by_users"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "product")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} saved {self.product}"


# ---------------------------------------------------------
# ⭐ RECENTLY VIEWED MODEL
# ---------------------------------------------------------
class RecentlyViewed(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recently_viewed",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="viewed_by",
    )
    viewed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "product")
        ordering = ("-viewed_at",)

    def __str__(self):
        return f"{self.user} viewed {self.product} at {self.viewed_at}"







