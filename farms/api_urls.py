from django.urls import path
from . import api_views

urlpatterns = [
    
    # -------------------------
    # FARMS
    # -------------------------
    path("farms/list/", api_views.ListFarmsView.as_view(), name="api_list_farms"),   # GET
    path("farms/add/", api_views.AddFarmView.as_view(), name="api_add_farm"),       # POST
    path("farms/detail/<int:id>/", api_views.FarmDetailView.as_view(), name="api_farm_detail"),  # GET
    path("farms/update/<int:id>/", api_views.UpdateFarmView.as_view(), name="api_farm_update"),  # PUT/PATCH
    path("farms/delete/<int:id>/", api_views.DeleteFarmView.as_view(), name="api_farm_delete"),  # DELETE
    # -------------------------
    # SHOPS
    # -------------------------
    path("shops/", api_views.ShopListView.as_view(), name="shop-list"),          # GET: list/search shops
    path("shops/<int:pk>/", api_views.ShopDetailView.as_view(), name="shop-detail"), 
    path("shops/my-requests/", api_views.MyRequestsView.as_view(), name="my-requests"),
 # GET: shop detail

    # ----------------------------
    # Farmer endpoints
    # ----------------------------
    path("shops/request/", api_views.RequestedShopCreateView.as_view(), name="shop-request"),  # POST: request a shop

    # ----------------------------
    # Admin endpoints
    # ----------------------------
    path("shops/create/", api_views.ShopCreateView.as_view(), name="shop-create"),  # POST: admin creates shop
    path("shops/requests/", api_views.RequestedShopListView.as_view(), name="requested-shop-list"),  # GET: list requests
    path("shops/requests/<int:pk>/approve/", api_views.approve_requested_shop, name="approve-requested-shop"),  # POST: approve
    path("shops/requests/<int:pk>/reject/", api_views.reject_requested_shop, name="reject-requested-shop"),    # POST: reject


    # -------------------------
    # NEARBY SHOPS
    # -------------------------
    path("nearby-shops/", api_views.NearbyShopsAPI.as_view(), name="api_nearby_shops"),

    # -------------------------
    # STATIC PAGES
    # -------------------------
    path("resources/", api_views.ResourcesAPI.as_view(), name="api_resources"),
    path("contact/", api_views.ContactAPI.as_view(), name="api_contact"),
]
