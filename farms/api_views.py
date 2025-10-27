from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.permissions import IsAuthenticated

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes

from .models import Farm
from shops.models import Shop,RequestedShop
from .serializers import FarmSerializer
from shops.serializers import ShopSerializer,RequestedShopSerializer
from .utils import geocode_address
import requests

ORS_API_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjUzMTEyNzYwNjczZjQwNTdhMTRlNTE1ZTJiYzcwZjI1IiwiaCI6Im11cm11cjY0In0="



# -------------------------
# FARM MANAGEMENT APIS
# -------------------------

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Farm
from .serializers import FarmSerializer
from .utils import geocode_address  # your geocoding helper


# Create a farm (user-owned)
class AddFarmView(generics.CreateAPIView):
    serializer_class = FarmSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        address = self.request.data.get("address")
        city = self.request.data.get("city")

        lat, lon = None, None
        if address and city:
            full_address = f"{address}, {city}"
            try:
                lat, lon = geocode_address(full_address)
            except Exception:
                # If geocoding fails, still save farm but without coords
                pass

        serializer.save(owner=self.request.user, latitude=lat, longitude=lon)


# List farms owned by the logged-in user
class ListFarmsView(generics.ListAPIView):
    serializer_class = FarmSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Farm.objects.filter(owner=self.request.user).order_by("-created_at")


# Retrieve details of a single farm (only if owned by user)
class FarmDetailView(generics.RetrieveAPIView):
    serializer_class = FarmSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        return Farm.objects.filter(owner=self.request.user)


# Update a farm (only if owned by user)
class UpdateFarmView(generics.UpdateAPIView):
    serializer_class = FarmSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        return Farm.objects.filter(owner=self.request.user)

    def perform_update(self, serializer):
        address = self.request.data.get("address")
        city = self.request.data.get("city")

        lat, lon = None, None
        if address and city:
            full_address = f"{address}, {city}"
            try:
                lat, lon = geocode_address(full_address)
            except Exception:
                pass

        serializer.save(latitude=lat, longitude=lon)


# Delete a farm (only if owned by user)
class DeleteFarmView(generics.DestroyAPIView):
    serializer_class = FarmSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        return Farm.objects.filter(owner=self.request.user)




# ----------------------------
# Public Shop Endpoints
# ----------------------------

class ShopListView(generics.ListAPIView):
    """
    List approved shops.
    Supports search by product (q) and city (?city=).
    """
    serializer_class = ShopSerializer

    def get_queryset(self):
        queryset = Shop.objects.all()
        search = self.request.query_params.get("q")
        city = self.request.query_params.get("city")

        if search:
            queryset = queryset.filter(products__icontains=search)
        if city:
            queryset = queryset.filter(city__icontains=city)

        return queryset


class ShopDetailView(generics.RetrieveAPIView):
    """Retrieve details of a single shop"""
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer


# ----------------------------
# Farmer Shop Requests
# ----------------------------

class RequestedShopCreateView(generics.CreateAPIView):
    """
    Farmers submit shop requests.
    Status defaults to 'pending'.
    """
    serializer_class = RequestedShopSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class MyRequestsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = RequestedShop.objects.filter(user=request.user)
        serializer = RequestedShopSerializer(qs, many=True)
        return Response(serializer.data)


# ----------------------------
# Admin Endpoints
# ----------------------------

class RequestedShopListView(generics.ListAPIView):
    """
    Admin can view all requested shops (pending/approved/rejected).
    """
    queryset = RequestedShop.objects.all().order_by("-created_at")
    serializer_class = RequestedShopSerializer
    permission_classes = [permissions.IsAdminUser]


@api_view(["POST"])
@permission_classes([permissions.IsAdminUser])
def approve_requested_shop(request, pk):
    """
    Admin approves a requested shop.
    Creates a Shop entry and updates request status.
    """
    req_shop = get_object_or_404(RequestedShop, pk=pk)

    if req_shop.status != "pending":
        return Response({"detail": "This request has already been processed."},
                        status=status.HTTP_400_BAD_REQUEST)

    # Create Shop from request
    shop = Shop.objects.create(
        name=req_shop.name,
        address=req_shop.address,
        city=req_shop.city,
        contact_number=req_shop.contact_number,
        products=req_shop.products,
    )

    req_shop.status = "approved"
    req_shop.save()

    return Response({
        "detail": "Shop approved and added to shops list.",
        "shop_id": shop.id
    }, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([permissions.IsAdminUser])
def reject_requested_shop(request, pk):
    """
    Admin rejects a requested shop.
    """
    req_shop = get_object_or_404(RequestedShop, pk=pk)

    if req_shop.status != "pending":
        return Response({"detail": "This request has already been processed."},
                        status=status.HTTP_400_BAD_REQUEST)

    req_shop.status = "rejected"
    req_shop.save()

    return Response({"detail": "Shop request rejected."}, status=status.HTTP_200_OK)


class ShopCreateView(generics.CreateAPIView):
    """
    Admin can directly create shops (bypasses request flow).
    """
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    permission_classes = [permissions.IsAdminUser]


# -------------------------
# NEARBY SHOPS
# -------------------------

class NearbyShopsAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        farms = Farm.objects.filter(owner=request.user)
        if not farms.exists():
            return Response({"nearby_shops": []})

        farm = farms.first()
        farm_coords = [farm.longitude, farm.latitude]
        shops = Shop.objects.all()
        shop_coords = [[shop.longitude, shop.latitude] for shop in shops if shop.latitude and shop.longitude]

        url = "https://api.openrouteservice.org/v2/matrix/driving-car"
        headers = {"Authorization": ORS_API_KEY, "Content-Type": "application/json"}
        body = {"locations": [farm_coords] + shop_coords, "metrics": ["distance", "duration"], "units": "km"}

        response = requests.post(url, json=body, headers=headers)
        nearby_shops = []
        if response.status_code == 200:
            data = response.json()
            distances = data["distances"][0][1:]
            durations = data["durations"][0][1:]

            for i, shop in enumerate(shops):
                if shop.latitude and shop.longitude and distances[i] <= 10:
                    nearby_shops.append({
                        "name": shop.name,
                        "distance_km": round(distances[i], 2),
                        "eta_minutes": round(durations[i] / 60, 1)  # convert seconds to minutes
                    })

        return Response({"nearby_shops": nearby_shops})

# -------------------------
# STATIC PAGES AS APIS
# -------------------------

class ResourcesAPI(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({"resources": "Here you can provide farming resources data"})


class ContactAPI(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({"contact": "Contact us at support@example.com"})
