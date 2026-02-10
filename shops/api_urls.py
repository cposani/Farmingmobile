# from django.urls import path
# from .api_views import ShopListView, ShopDetailView,ShopCreateView

# urlpatterns = [
#     path('list/', ShopListView.as_view(), name='shop-list'),
#     path('detail/<int:id>/', ShopDetailView.as_view(), name='shop-detail'),
#     path('create/', ShopCreateView.as_view(), name='shop-create'),
# ]

# market/urls.py

from django.conf import settings
from django.conf.urls.static import static

from django.urls import path
from .api_views import (
    ProductListView, ProductDetailView, ProductCreateView, ProductUpdateView,
    ProductPendingListView, ProductRejectedListView,
    ProductApproveView, ProductRejectView, ProductResubmitView,
    ProductDeleteView, MyProductsView,AdminMyProductsView,SavedProductListView, SavedProductToggleView,RecentlyViewedListView, AddRecentlyViewedView)

urlpatterns = [
    # Public
    path("products/list/", ProductListView.as_view(), name="product-list"),
    path("products/detail/<int:id>/", ProductDetailView.as_view(), name="product-detail"),

    # User actions
    path("saved/list/", SavedProductListView.as_view(), name="saved-list"), 
    path("saved/toggle/", SavedProductToggleView.as_view(), name="saved-toggle"),
    path("products/create/", ProductCreateView.as_view(), name="product-create"),
    path("products/update/<int:id>/", ProductUpdateView.as_view(), name="product-update"),
    path("products/resubmit/<int:id>/", ProductResubmitView.as_view(), name="product-resubmit"),
    path("products/my-products/", MyProductsView.as_view(), name="my-products"),
    path("recently-viewed/", RecentlyViewedListView.as_view(), name="recently-viewed-list"), 
    path("recently-viewed/add/", AddRecentlyViewedView.as_view(), name="recently-viewed-add"),

    # Admin moderation
    path("products/admin-my-products/", AdminMyProductsView.as_view(), name="admin-my-products"),
    path("products/pending/", ProductPendingListView.as_view(), name="product-pending"),
    path("products/rejected/", ProductRejectedListView.as_view(), name="product-rejected"),
    path("products/approve/<int:id>/", ProductApproveView.as_view(), name="product-approve"),
    path("products/reject/<int:id>/", ProductRejectView.as_view(), name="product-reject"),
    path("products/delete/<int:id>/", ProductDeleteView.as_view(), name="product-delete"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)