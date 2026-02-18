from django.urls import path
from . import api_views 
from .api_views import track_open
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # -------------------------
    # AUTHENTICATION
    # -------------------------
    path("register/", api_views.RegisterAPI.as_view(), name="api_register"),
    path("verify-registration-otp/", api_views.VerifyRegistrationOTPAPI.as_view(), name="verify_registration_otp"),
    path("login/", api_views.LoginAPI.as_view(), name="api_login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("request-otp/", api_views.RequestOTPAPI.as_view(), name="request_otp"),
    path("verify-otp/", api_views.VerifyOTPAPI.as_view(), name="verify_otp"),
    path("reset-password/", api_views.ResetPasswordAPI.as_view(), name="reset_password"),
    path("profile/update/", api_views.ProfileUpdateView.as_view()),
    path("profile/me/", api_views.ProfileMeView.as_view()),
    path("profile/change-password/", api_views.ChangePasswordView.as_view()),
    path("profile/request-email-change/", api_views.RequestEmailChangeView.as_view()),
    path("profile/confirm-email-change/", api_views.ConfirmEmailChangeView.as_view()),
    path("track-open/", track_open, name="track-open"),




    

]