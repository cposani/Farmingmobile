from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Profile, UserActivity



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

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = (
        "user_account",
        "user_full_name",
        "date",
        "opens_count",
        "logins_count",
    )
    list_filter = ("date", "user")

    def user_account(self, obj):
        # Show username or email (same as Products admin)
        return obj.user.username or obj.user.email
    user_account.short_description = "Seller (account)"

    def user_full_name(self, obj):
        # Show actual seller name
        first = obj.user.first_name or ""
        last = obj.user.last_name or ""
        full = f"{first} {last}".strip()
        return full if full else "—"
    user_full_name.short_description = "Seller name"


# Replace default User admin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
