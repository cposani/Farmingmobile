from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Farm

class FarmAdmin(admin.ModelAdmin):
    exclude = ['owner'] 
    list_display = ['name', 'owner', 'address', 'city', 'size']
    readonly_fields = ['owner'] # hide owner field in admin form

    def save_model(self, request, obj, form, change):
        if not obj.owner:
            obj.owner = request.user  # assign logged-in admin as owner
        obj.save()

admin.site.register(Farm, FarmAdmin)

