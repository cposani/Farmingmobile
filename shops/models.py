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

class Product(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    name = models.CharField(max_length=120)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=120)
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

    # ✅ Image upload
    image = models.ImageField(upload_to="products/", null=True, blank=True)
    seller_name=models.CharField(max_length=50,blank=True,null=True)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="products")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    approved_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="approved_products"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.status})"

from django.conf import settings
from django.db import models
from .models import Product  # adjust import if Product is elsewhere

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



























# # Create your models here.
# from django.db import models

# class Shop(models.Model):
#     name = models.CharField(max_length=100)
#     address = models.CharField(max_length=255)
#     city = models.CharField(max_length=100)
#     latitude = models.FloatField(null=True, blank=True)
#     longitude = models.FloatField(null=True, blank=True)
#     contact_number = models.CharField(max_length=15, null=True, blank=True)
#     products = models.TextField(help_text="Comma-separated list of products", blank=True, null=True)

#     # Per-day hours
#     monday_hours = models.CharField(max_length=50, blank=True, null=True, help_text="e.g. 9 AM - 6 PM or Closed")
#     tuesday_hours = models.CharField(max_length=50, blank=True, null=True)
#     wednesday_hours = models.CharField(max_length=50, blank=True, null=True)
#     thursday_hours = models.CharField(max_length=50, blank=True, null=True)
#     friday_hours = models.CharField(max_length=50, blank=True, null=True)
#     saturday_hours = models.CharField(max_length=50, blank=True, null=True)
#     sunday_hours = models.CharField(max_length=50, blank=True, null=True)

#     def __str__(self):
#         return f"{self.name} ({self.city})"

#     def save(self, *args, **kwargs):
#         if (not self.latitude or not self.longitude) and (self.address and self.city):
#             full_address = f"{self.address}, {self.city}"
#             lat, lon = geocode_address(full_address)
#             if lat and lon:
#                 self.latitude = lat
#                 self.longitude = lon
#         super().save(*args, **kwargs)


# class RequestedShop(models.Model):
#     STATUS_CHOICES = [
#         ('pending', 'Pending'),
#         ('approved', 'Approved'),
#         ('rejected', 'Rejected'),
#     ]

#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     name = models.CharField(max_length=100)
#     address = models.CharField(max_length=255)
#     city = models.CharField(max_length=100)
#     contact_number = models.CharField(max_length=15, null=True, blank=True)
#     products = models.TextField(help_text="Comma-separated list of products", blank=True, null=True)
#     status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.name} ({self.city}) - {self.status}"
