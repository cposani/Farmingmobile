from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework import status
from .forms import CustomUserCreationForm
from django.utils.encoding import force_bytes
from django.conf import settings


# 🌱 Homepage
def home_view(request):
    return render(request, 'home.html')

# 🧑‍🌾 Farmer Registration (Template + Email Verification)
import logging
logger = logging.getLogger(__name__)


from django.conf import settings
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponse
from django.shortcuts import render
from .forms import CustomUserCreationForm
import logging

logger = logging.getLogger(__name__)

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.is_active = False
                user.email = form.cleaned_data.get('email')
                user.save()

                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)

                # 🌍 Use localhost in DEBUG, production domain otherwise
                if settings.DEBUG==True:
                    protocol = 'http'
                    domain = 'localhost:8000'
                else:
                    protocol = 'https'
                    domain = 'organic-farming-app.onrender.com'

                link = f"{protocol}://{domain}/activate/{uid}/{token}/"

                # 📧 Email logic based on DEBUG
                send_mail(
                        subject='Verify your email',
                        message=f'Hello, {user.username}, Welcome to Organic Farming!\nClick to verify: {link}',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        fail_silently=False,
                    )

                return render(request, 'email_sent.html', {'email': user.email})
            except Exception as e:
                logger.error(f"Registration error: {e}")
                return HttpResponse("Something went wrong", status=500)
        else:
            print("Form is NOT valid")
            print(form.errors.as_data())
    else:
        form = CustomUserCreationForm()

    return render(request, 'register.html', {'form': form})



# 🔐 Login Page
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

# 📧 Email Verification via Template

from django.utils.encoding import force_str
def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, 'activation_success.html', {'username': user.username})
    else:
        return render(request, 'activation_failed.html')



#farm management views

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Farm
from shops.models import Shop
from .serializers import FarmSerializer
from shops.serializers import ShopSerializer
from .utils import geocode_address, haversine
import requests
from .forms import FarmForm
from django.shortcuts import get_object_or_404



ORS_API_KEY = 'eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjUzMTEyNzYwNjczZjQwNTdhMTRlNTE1ZTJiYzcwZjI1IiwiaCI6Im11cm11cjY0In0='



# @login_required
# def dashboard_view(request):
#     farms = Farm.objects.filter(owner=request.user)
#     return render(request, 'dashboard.html', {'farms': farms,'username': request.user.username})

@login_required
def dashboard_view(request):
    farms = Farm.objects.filter(owner=request.user)
    farm_count = farms.count()

    nearby_shops = []
    featured_tip = "How to compost efficiently 🌿"

    if farm_count > 0:
        farm = farms.first()
        farm_coords = [farm.longitude, farm.latitude]
        shops = Shop.objects.all()
        shop_coords = [[shop.longitude, shop.latitude] for shop in shops]

        url = "https://api.openrouteservice.org/v2/matrix/driving-car"
        headers = {
            "Authorization": ORS_API_KEY,
            "Content-Type": "application/json"
        }
        body = {
            "locations": [farm_coords] + shop_coords,
            "metrics": ["distance", "duration"],
            "units": "km"
        }

        response = requests.post(url, json=body, headers=headers)
        if response.status_code == 200:
            data = response.json()
            distances = data["distances"][0][1:]
            durations = data["durations"][0][1:]

            for i, shop in enumerate(shops):
                if distances[i] <= 10:
                    nearby_shops.append({
                        "name": shop.name,
                        "distance_km": round(distances[i], 2),
                        "eta_minutes": round(durations[i], 1)
                    })

    return render(request, 'dashboard.html', {
        'username': request.user.username,
        'farm_count': farm_count,
        'farms': farms,
        'nearby_shops': nearby_shops,
        'featured_tip': featured_tip
    })



def resources_view(request):
    return render(request, 'resources.html')

def contact_view(request):
    return render(request, 'contact.html')

















@login_required
def farm_register_view(request):
    if request.method == 'POST':
        form = FarmForm(request.POST)
        if form.is_valid():
            farm = form.save(commit=False)
            farm.owner = request.user
            lat, lon = geocode_address(farm.address)
            farm.latitude = lat
            farm.longitude = lon
            print("Creating farm for:", request.user.username)
            farm.save()
            print("Farm saved with owner:", farm.owner.username)
            print("request.user.id:", request.user.id)
            print("request.user.username:", request.user.username)

            return redirect('dashboard')
    else:
        form = FarmForm()
    return render(request, 'farm_register.html', {'form': form})

@login_required
def view_farms(request):
    farms = Farm.objects.filter(owner=request.user)
    return render(request, 'view_farms.html', {'farms': farms})


@login_required
def edit_farm(request, farm_id):
    """Edit a specific farm owned by the logged-in user"""
    farm = get_object_or_404(Farm, id=farm_id, owner=request.user)

    if request.method == 'POST':
        form = FarmForm(request.POST, instance=farm)
        if form.is_valid():
            farm = form.save(commit=False)
            # re-geocode if address changed
            lat, lon = geocode_address(farm.address)
            farm.latitude = lat
            farm.longitude = lon
            farm.save()
            return redirect('view_farms')
    else:
        form = FarmForm(instance=farm)

    return render(request, 'edit_farm.html', {'form': form, 'farm': farm})



from datetime import datetime
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import requests
from farms.models import Farm
from shops.models import Shop

def format_duration(seconds):
    """Convert ORS duration (in seconds) into Google Maps style text."""
    minutes = int(round(seconds / 60))  # ORS gives seconds
    if minutes < 60:
        return f"{minutes} min"
    hours, mins = divmod(minutes, 60)
    if mins == 0:
        return f"{hours} hr"
    return f"{hours} hr {mins} min"

@login_required
def nearby_shops_view(request):
    farms = Farm.objects.filter(owner=request.user)

    farm_id = request.GET.get('farm_id')
    radius = float(request.GET.get('radius', 10))
    radius_options = [5, 15, 25, 50]

    farm = None
    nearby = []

    if farm_id:
        try:
            farm = Farm.objects.get(id=farm_id, owner=request.user)
        except Farm.DoesNotExist:
            return render(request, 'nearby_shops.html', {
                'error': 'Farm not found',
                'farms': farms,
                'radius_options': radius_options,
                'radius': int(radius)
            })

        farm_coords = [farm.longitude, farm.latitude]
        shops = Shop.objects.all()
        shop_coords = [[shop.longitude, shop.latitude] for shop in shops if shop.latitude and shop.longitude]

        url = "https://api.openrouteservice.org/v2/matrix/driving-car"
        headers = {
            "Authorization": ORS_API_KEY,
            "Content-Type": "application/json"
        }
        body = {
            "locations": [farm_coords] + shop_coords,
            "metrics": ["distance", "duration"],
            "units": "km"
        }

        response = requests.post(url, json=body, headers=headers)
        if response.status_code == 200:
            data = response.json()
            distances = data["distances"][0][1:]
            durations = data["durations"][0][1:]

            for i, shop in enumerate(shops):
                if shop.latitude and shop.longitude:  # skip invalid shops
                    if distances[i] <= radius:
                        shop.distance_km = round(distances[i], 2)
                        shop.eta_text = format_duration(durations[i])  # formatted ETA
                        nearby.append(shop)

            nearby.sort(key=lambda x: x.distance_km)
        else:
            return render(request, 'nearby_shops.html', {
                'error': 'ORS API failed',
                'farms': farms,
                'radius_options': radius_options,
                'radius': int(radius)
            })

    today = timezone.localtime().strftime('%a')

    return render(request, 'nearby_shops.html', {
        'farm': farm,
        'farms': farms,
        'shops': nearby,
        'radius': int(radius),
        'radius_options': radius_options,
        'today': today
    })


from .forms import RequestedShopForm
@login_required
def request_shop_view(request):
    if request.method == "POST":
        form = RequestedShopForm(request.POST)
        if form.is_valid():
            requested_shop = form.save(commit=False)
            requested_shop.user = request.user
            requested_shop.save()
            return redirect("dashboard")
    else:
        form = RequestedShopForm()
    return render(request, "request_shop.html", {"form": form})




from django.db.models.signals import post_save
from django.dispatch import receiver
from shops.models import RequestedShop
from django.core.mail import send_mail

@receiver(post_save, sender=RequestedShop)
def notify_user_on_status_change(sender, instance, **kwargs):
    if instance.status in ["approved", "rejected"]:
        subject = "Your shop request has been reviewed"
        if instance.status == "approved":
            message = f"✅ Your requested shop '{instance.name}' has been approved!"
        else:
            message = f"❌ Your requested shop '{instance.name}' was not approved."
        send_mail(subject, message, "posanigufus2023@gmail.com", [instance.user.email])





from django.contrib.auth import logout

def logout_view(request):
    logout(request)
    return render(request, 'logged_out.html')

    
