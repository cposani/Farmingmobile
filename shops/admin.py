from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Shop

@admin.register(Shop)

class ShopAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "contact_number")
    fieldsets = (
        (None, {
            "fields": ("name", "address", "city", "latitude", "longitude", "contact_number")
        }),
        ("Hours of Operation", {
            "fields": (
                "monday_hours", "tuesday_hours", "wednesday_hours",
                "thursday_hours", "friday_hours", "saturday_hours", "sunday_hours"
            )
        }),
    )


from django.contrib import admin
from .models import RequestedShop

@admin.register(RequestedShop)
class RequestedShopAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "status", "user", "created_at")
    list_filter = ("status", "city")
    search_fields = ("name", "address", "city")


