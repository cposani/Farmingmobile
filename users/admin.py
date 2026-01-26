from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Profile


# Profile inline inside User admin
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "Profile"


# Custom User admin
class UserAdmin(BaseUserAdmin):
    list_display = (
        "id",
        "username",
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
        "is_superuser",
        "last_login",
        "date_joined",
    )

    search_fields = ("username", "email", "first_name", "last_name")

    list_filter = ("is_active", "is_staff", "is_superuser")

    ordering = ("-date_joined",)

    inlines = (ProfileInline,)


# Replace default User admin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
