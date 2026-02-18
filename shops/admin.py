


from django.contrib import admin
from django.utils.html import format_html
from .models import Product, ProductImage


# ⭐ Inline for multiple images
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    readonly_fields = ("preview",)

    def preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:60px;width:60px;object-fit:cover;border-radius:6px;" />',
                obj.image.url,
            )
        return "-"
    preview.short_description = "Preview"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    readonly_fields = ("seller_full_name", "approved_by", "created_at", "updated_at", "local_created_at")

    inlines = [ProductImageInline]

    # Columns in list view
    list_display = (
        "id",
        "name",
        "seller_full_name",
        "seller_name",
        "price",
        "status",
        "thumbnail",
        "created_at",
        "local_created_at"
    )

    list_display_links = ("id", "name")

    list_filter = ("status", "created_at", "seller_name")

    search_fields = (
        "name",
        "description",
        "seller__username",
        "seller__email",
        "seller__first_name",
        "seller__last_name",
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
        "seller_full_name",
        "seller_name",
        "status",
        "approved_by",
        "created_at",
        "updated_at",
    )

    actions = ["approve_products", "reject_products","regeocode_products"]

    #Geocode action to update lat/lon based on location using Open-Meteo API
    def regeocode_products(self, request, queryset):
        updated = 0
        for product in queryset:
            if product.location:
                # Force re-geocode by clearing coords then saving
                product.latitude = None
                product.longitude = None
                product.save()
                updated += 1
        self.message_user(request, f"Re-geocoded {updated} product(s).")

    regeocode_products.short_description = "Re-geocode selected products using LocationIQ"

    # ---------- DISPLAY HELPERS ----------

    def seller_full_name(self, obj):
        if not obj or not obj.seller_id:
            return "-"
        first = (obj.seller.first_name or "").strip()
        last = (obj.seller.last_name or "").strip()
        full = f"{first} {last}".strip()
        return full or obj.seller.username

    seller_full_name.short_description = "Seller (account)"

    # ⭐ Thumbnail from first ProductImage
    def thumbnail(self, obj):
        first_image = obj.images.first()
        if first_image:
            return format_html(
                '<img src="{}" style="height:50px;width:50px;object-fit:cover;border-radius:4px;" />',
                first_image.image.url,
            )
        return "-"
    thumbnail.short_description = "Image"

    # ---------- ADMIN CREATE / UPDATE LOGIC ----------

    def save_model(self, request, obj, form, change):
        if not change and obj.seller_id is None:
            obj.seller = request.user

        if obj.status == Product.Status.APPROVED and obj.approved_by is None:
            obj.approved_by = request.user

        super().save_model(request, obj, form, change)

    # ---------- BULK ACTIONS ----------

    def approve_products(self, request, queryset):
        updated = 0
        for product in queryset:
            if product.status != Product.Status.APPROVED:
                product.status = Product.Status.APPROVED
                if product.approved_by is None:
                    product.approved_by = request.user
                product.save()
                updated += 1
        self.message_user(request, f"{updated} product(s) approved.")
    approve_products.short_description = "Approve selected products"

    def reject_products(self, request, queryset):
        updated = 0
        for product in queryset:
            if product.status != Product.Status.REJECTED:
                product.status = Product.Status.REJECTED
                product.save()
                updated += 1
        self.message_user(request, f"{updated} product(s) rejected.")
    reject_products.short_description = "Reject selected products"


