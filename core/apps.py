from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        # Force rebind of default_storage to Cloudinary
        from django.core.files.storage import default_storage
        from cloudinary_storage.storage import MediaCloudinaryStorage
        default_storage._wrapped = MediaCloudinaryStorage()
