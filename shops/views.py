from django.shortcuts import render

# Create your views here.
from rest_framework import generics,permissions
from .models import Shop
from .serializers import ShopListSerializer
from .utils import geocode_address


class ShopCreateView(generics.CreateAPIView):
    queryset = Shop.objects.all()
    serializer_class = ShopListSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_create(self, serializer):
        address = self.request.data.get('address')
        lat, lon = geocode_address(address)
        serializer.save(latitude=lat, longitude=lon)

        
class ShopListView(generics.ListAPIView):
    queryset = Shop.objects.all()
    serializer_class = ShopListSerializer

class ShopDetailView(generics.RetrieveAPIView):
    queryset = Shop.objects.all()
    serializer_class = ShopListSerializer
    lookup_field = 'id'
