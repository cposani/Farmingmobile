from django.urls import path
from .views import ShopListView, ShopDetailView,ShopCreateView

urlpatterns = [
    path('list/', ShopListView.as_view(), name='shop-list'),
    path('detail/<int:id>/', ShopDetailView.as_view(), name='shop-detail'),
    path('create/', ShopCreateView.as_view(), name='shop-create'),
]
