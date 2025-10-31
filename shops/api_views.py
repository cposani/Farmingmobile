from django.shortcuts import render

# Create your views here.
from rest_framework import generics,permissions
from .models import Shop
from .serializers import ShopSerializer
from .utils import geocode_address

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Product
from .serializers import ProductSerializer
from rest_framework import filters

# ✅ Public: list approved products

class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description", "location", "seller__username"]
    ordering_fields = ["price", "created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return Product.objects.filter(status=Product.Status.APPROVED)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context



# ✅ Public: product detail
class ProductDetailView(generics.RetrieveAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "id"

    def get_queryset(self):
        return Product.objects.all()

import logging
from django.core.files.storage import default_storage
from rest_framework.parsers import MultiPartParser, FormParser
# ✅ Create product (user → pending, admin → approved)
class ProductCreateView(generics.CreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        logging.warning(f"Using storage backend: {default_storage.__class__.__name__}")
        return context


    



# ✅ Update product (user: only pending/rejected; admin: any)
class ProductUpdateView(generics.UpdateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        return Product.objects.all()

    def update(self, request, *args, **kwargs):
        product = self.get_object()

        # Admin can always update
        if request.user.is_staff:
            return super().update(request, *args, **kwargs)

        # User must be the owner
        if product.seller_id != request.user.id:
            return Response({"detail": "Not your product."}, status=status.HTTP_403_FORBIDDEN)

        # User cannot edit approved
        if product.status == Product.Status.APPROVED:
            return Response({"detail": "You cannot edit an approved product."}, status=status.HTTP_403_FORBIDDEN)

        # Allowed: pending or rejected
        return super().update(request, *args, **kwargs)


# ✅ Admin: list pending
class ProductPendingListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return Product.objects.filter(status=Product.Status.PENDING).order_by("-created_at")


# ✅ Admin: list rejected
class ProductRejectedListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return Product.objects.filter(status=Product.Status.REJECTED).order_by("-created_at")


# ✅ Admin: approve
class ProductApproveView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def patch(self, request, id):
        product = get_object_or_404(Product, id=id)
        product.status = Product.Status.APPROVED
        product.approved_by = request.user
        product.save(update_fields=["status", "approved_by", "updated_at"])
        return Response({"status": "APPROVED"})


# ✅ Admin: reject
class ProductRejectView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def patch(self, request, id):
        product = get_object_or_404(Product, id=id)
        product.status = Product.Status.REJECTED
        product.approved_by = request.user
        product.save(update_fields=["status", "approved_by", "updated_at"])
        return Response({"status": "REJECTED"})

# ✅ Admin: list their own products
class AdminMyProductsView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return Product.objects.filter(seller=self.request.user).order_by("-created_at")



# ✅ User: resubmit rejected product
class ProductResubmitView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, id):
        product = get_object_or_404(Product, id=id)

        if request.user.is_staff:
            return Response({"detail": "Admins don't need to resubmit."}, status=status.HTTP_400_BAD_REQUEST)

        if product.seller_id != request.user.id:
            return Response({"detail": "Not your product."}, status=status.HTTP_403_FORBIDDEN)

        if product.status != Product.Status.REJECTED:
            return Response({"detail": "Only rejected products can be resubmitted."}, status=status.HTTP_400_BAD_REQUEST)

        product.status = Product.Status.PENDING
        product.approved_by = None
        product.save(update_fields=["status", "approved_by", "updated_at"])
        return Response({"status": "PENDING"})


# ✅ Admin-only delete
class ProductDeleteView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def delete(self, request, id):
        product = get_object_or_404(Product, id=id)
        product.delete()
        return Response({"detail": "Product deleted by admin."}, status=status.HTTP_204_NO_CONTENT)


# ✅ User: list their own products with status
class MyProductsView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Product.objects.filter(seller=self.request.user).order_by("-created_at")


    
class ShopCreateView(generics.CreateAPIView):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_create(self, serializer):
        address = self.request.data.get('address')
        lat, lon = geocode_address(address)
        serializer.save(latitude=lat, longitude=lon)

        
class ShopListView(generics.ListAPIView):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer

class ShopDetailView(generics.RetrieveAPIView):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    lookup_field = 'id'
