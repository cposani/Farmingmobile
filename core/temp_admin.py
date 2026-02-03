from django.http import HttpResponse
from django.contrib.auth import get_user_model

def create_admin(request):
    User = get_user_model()

    try:
        if User.objects.filter(username="admin").exists():
            return HttpResponse("Admin already exists")

        User.objects.create_superuser(
            username="natural@7",
            email="charithaposani@gmail.com",
            password="Harekrishna@7"
        )
        return HttpResponse("Admin created successfully")

    except Exception as e:
        return HttpResponse(f"Error: {str(e)}")
