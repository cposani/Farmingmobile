from django.contrib import admin

# Register your models here.

from django.contrib import admin
from django.utils.html import format_html
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Columns in list view
    list_display = (
        "id",
        "name",
        "seller",
        "seller_name",
        "price",
        "status",
        "thumbnail",
        "created_at",
    )

    list_display_links = ("id", "name")

    # Filters on right side
    list_filter = ("status", "created_at", "seller")

    # Search bar
    search_fields = (
        "name",
        "description",
        "seller__username",
        "seller__email",
        "seller_name",
        "location",
        "contact",
    )

    ordering = ("-created_at",)

    # Fields shown in product detail page
    fields = (
        "name",
        "description",
        "price",
        "location",
        "latitude",
        "longitude",
        "contact",
        "image",
        "seller",
        "seller_name",
        "status",
        "approved_by",
        "created_at",
        "updated_at",
    )

    readonly_fields = ("created_at", "updated_at")

    # Bulk actions
    actions = ["approve_products", "reject_products"]

    # Thumbnail preview
    def thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:50px;width:50px;object-fit:cover;border-radius:4px;" />',
                obj.image.url,
            )
        return "-"
    thumbnail.short_description = "Image"

    # Bulk Approve
    def approve_products(self, request, queryset):
        updated = queryset.update(status=Product.Status.APPROVED)
        self.message_user(request, f"{updated} product(s) approved.")
    approve_products.short_description = "Approve selected products"

    # Bulk Reject
    def reject_products(self, request, queryset):
        updated = queryset.update(status=Product.Status.REJECTED)
        self.message_user(request, f"{updated} product(s) rejected.")
    reject_products.short_description = "Reject selected products"

