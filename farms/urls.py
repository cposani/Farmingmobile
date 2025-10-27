from django.urls import path
from .views import (
    home_view, register_view, login_view, activate_account,
    dashboard_view, farm_register_view, nearby_shops_view,logout_view,view_farms,edit_farm,resources_view,contact_view,request_shop_view
)

urlpatterns = [
    path('', home_view, name='home'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('activate/<uidb64>/<token>/', activate_account, name='activate'),

    # 🌱 Farm management UI
    path('dashboard/', dashboard_view, name='dashboard'),
    path('farms/register/', farm_register_view, name='farm_register'),
    path('farms/nearby/', nearby_shops_view, name='nearby_shops'),
    path('shops/request/', request_shop_view, name='request_shop'),
    path('logout/', logout_view, name='logout'),
    path('farms/view', view_farms, name='view_farms'),
    path('farms/<int:farm_id>/edit/', edit_farm, name='edit_farm'),
    path('resources/', resources_view, name='resources'),
    path('contact/', contact_view, name='contact'),
    

]

