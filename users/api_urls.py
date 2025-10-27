from django.urls import path
from . import api_views

urlpatterns = [
    # -------------------------
    # AUTHENTICATION
    # -------------------------
    path("register/", api_views.RegisterAPI.as_view(), name="api_register"),
    path("verify-registration-otp/", api_views.VerifyRegistrationOTPAPI.as_view(), name="verify_registration_otp"),
    path("login/", api_views.LoginAPI.as_view(), name="api_login"),
    path("request-otp/", api_views.RequestOTPAPI.as_view(), name="request_otp"),
    path("verify-otp/", api_views.VerifyOTPAPI.as_view(), name="verify_otp"),
    path("reset-password/", api_views.ResetPasswordAPI.as_view(), name="reset_password"),
    # path("forgot-username/request-otp/", api_views.ForgotUsernameOTPAPI.as_view(), name="forgot_username_request_otp"),
    # path("forgot-username/verify-otp/", api_views.VerifyUsernameOTPAPI.as_view(), name="forgot_username_verify_otp"),

]