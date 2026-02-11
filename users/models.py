from django.db import models

# Create your models here.

from django.contrib.auth.models import User
from django.utils import timezone


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone = models.CharField(max_length=13, blank=True)

    def __str__(self):
        return f"{self.user.username} Profile"
    


from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class PasswordResetOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="password_otps")
    code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=32, default="password_reset")  # future-proof
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["user", "code", "purpose", "created_at"]),
        ]

    def is_valid(self, ttl_minutes=5):
        return (not self.used) and (timezone.now() <= self.created_at + timedelta(minutes=ttl_minutes))