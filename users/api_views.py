from django.shortcuts import render

# Create your views here.
# -------------------------
# AUTHENTICATION APIS
# -------------------------

# users/api_views.py
import re
from django.conf import settings
from django.core.mail import send_mail, BadHeaderError
from django.contrib.auth.models import User
from django.db import transaction
from django.contrib.auth.tokens import default_token_generator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Profile
import uuid
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
import datetime
from .serializers import UserSerializer
from django.contrib.auth import get_user_model

def validate_password_policy(pwd: str) -> bool:
    # At least 8 chars, one uppercase, one number
    return bool(re.match(r"^(?=.*[A-Z])(?=.*\d).{8,}$", pwd or ""))

def is_valid_phone(phone: str) -> bool:
    return bool(re.fullmatch(r"[0-9+\-\s()]{7,20}", phone or ""))

User = get_user_model()

def generate_otp():
    return f"{random.randint(100000, 999999)}"

class RegisterAPI(APIView):
    permission_classes = [permissions.AllowAny]

    @transaction.atomic
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        phone = request.data.get("phone")

        if not email:
            return Response({"error": "Email required"}, status=status.HTTP_400_BAD_REQUEST)

        email = email.lower().strip()
        existing = User.objects.filter(email__iexact=email).first()

        # Case 1: Existing user
        if existing:
            if existing.is_active:
                return Response({"error": "Email already registered"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Resend OTP for inactive user
                code = generate_otp()
                PasswordResetOTP.objects.create(user=existing, code=code, purpose="registration")

                subject = "Verify your account"
                message = (
                    f"Hello {existing.first_name or ''},\n\n"
                    f"Your OTP code is: {code}\n"
                    f"This code expires in {getattr(settings, 'OTP_TTL_MINUTES', 5)} minutes.\n\n"
                    f"Enter this code in the app to activate your account."
                )
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [existing.email])
                return Response({"message": "OTP re-sent to email."}, status=status.HTTP_200_OK)

        # Case 2: New user registration
        if not password or not first_name or not last_name or not phone:
            return Response(
                {"error": "All fields required for new registration"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if Profile.objects.filter(phone=phone).exists():
            return Response({"error": "Phone already registered"}, status=status.HTTP_400_BAD_REQUEST)

        auto_username = f"user_{uuid.uuid4().hex[:10]}"

        user = User.objects.create_user(
            username=auto_username,
            email=email,
            password=password,
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            is_active=False,
        )
        user.profile.phone = phone.strip()
        user.profile.save()

        code = generate_otp()
        PasswordResetOTP.objects.create(user=user, code=code, purpose="registration")

        subject = "Verify your account"
        message = (
            f"Hello {first_name},\n\n"
            f"Your OTP code is: {code}\n"
            f"This code expires in {getattr(settings, 'OTP_TTL_MINUTES', 5)} minutes.\n\n"
            f"Enter this code in the app to activate your account."
        )
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

        return Response({"message": "User created. OTP sent to email."}, status=status.HTTP_201_CREATED)

    
class VerifyRegistrationOTPAPI(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")

        if not email or not otp:
            return Response({"error": "Email and OTP required"}, status=400)

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response({"error": "Invalid email"}, status=400)

        try:
            otp_obj = PasswordResetOTP.objects.filter(
                user=user, code=otp, purpose="registration", used=False
            ).latest("created_at")
        except PasswordResetOTP.DoesNotExist:
            return Response({"error": "Invalid OTP"}, status=400)

        ttl = getattr(settings, "OTP_TTL_MINUTES", 5)
        if not otp_obj.is_valid(ttl_minutes=ttl):
            return Response({"error": "OTP expired"}, status=400)

        # Mark OTP as used
        otp_obj.used = True
        otp_obj.save()

        # Activate user
        user.is_active = True
        user.save()

        return Response({"message": "Account verified successfully. You can now log in."}, status=200)

# users/api_views.py
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from .models import Profile

class LoginAPI(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        phone = request.data.get("phone")
        password = request.data.get("password")

        if not password or (not email and not phone):
            return Response({"error": "Email/Phone and password required"}, status=status.HTTP_400_BAD_REQUEST)

        user = None
        if email:
            user = User.objects.filter(email__iexact=email).first()
        elif phone:
            profile = Profile.objects.filter(phone=phone).first()
            if profile:
                user = profile.user

        if not user:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=user.username, password=password)
        if not user:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
        if not user.is_active:
            return Response({"error": "Account not activated"}, status=status.HTTP_403_FORBIDDEN)

        # Return token
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "message": "Login successful",
            "token": token.key,
            "user": {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "phone": user.profile.phone,
                "user": UserSerializer(user).data,
            }
        })

# users/api_views.py
import random
from django.conf import settings
from django.core.mail import send_mail, BadHeaderError
from django.utils import timezone
from datetime import timedelta

from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from .models import PasswordResetOTP

#after user created
#otp api's for forgot password recovery.
def generate_otp():
    return f"{random.randint(100000, 999999)}"

def can_issue_otp(user):
    one_hour_ago = timezone.now() - timedelta(hours=1)
    count = PasswordResetOTP.objects.filter(user=user, created_at__gte=one_hour_ago).count()
    return count < getattr(settings, "OTP_MAX_PER_HOUR", 5)

def send_otp_email(user, code, subject_prefix="Password"):
    subject = f"{subject_prefix} Reset OTP"
    message = (
        f"Hello {user.first_name},\n\n"
        f"Your OTP code is: {code}\n"
        f"This code expires in {getattr(settings, 'OTP_TTL_MINUTES', 5)} minutes.\n\n"
        f"If you didn't request this, you can ignore this email."
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)

class RequestOTPAPI(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            # Do not reveal existence
            return Response({"message": "If an account exists, an OTP has been sent."}, status=status.HTTP_200_OK)

        if not can_issue_otp(user):
            # Avoid enumeration; keep generic response
            return Response({"message": "If an account exists, an OTP has been sent."}, status=status.HTTP_200_OK)

        code = generate_otp()
        PasswordResetOTP.objects.create(user=user, code=code, purpose="password_reset")
        try:
            send_otp_email(user, code, subject_prefix="Password")
        except BadHeaderError:
            return Response({"error": "Invalid email header"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception:
            # Log exception in real apps
            return Response({"error": "Email sending failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "If an account exists, an OTP has been sent."}, status=status.HTTP_200_OK)

class VerifyOTPAPI(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")
        if not email or not otp:
            return Response({"error": "Email and OTP required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            latest = PasswordResetOTP.objects.filter(
                user=user, code=otp, purpose="password_reset", used=False
            ).latest("created_at")
        except PasswordResetOTP.DoesNotExist:
            return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

        ttl = getattr(settings, "OTP_TTL_MINUTES", 5)
        if not latest.is_valid(ttl_minutes=ttl):
            return Response({"error": "OTP expired"}, status=status.HTTP_400_BAD_REQUEST)

        # Mark as used, and issue a temporary verification token (short-lived)
        latest.used = True
        latest.save()

        # For simplicity, return a short-lived token derived from the OTP record id.
        # In production, prefer signing with its timestamp for expiry.
        temp_token = f"otp-{latest.id}"
        return Response({"message": "OTP verified", "otp_token": temp_token}, status=status.HTTP_200_OK)

class ResetPasswordAPI(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        new_password = request.data.get("new_password")
        otp_token = request.data.get("otp_token")

        if not email or not new_password or not otp_token:
            return Response({"error": "Email, new_password, and otp_token required"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate token structure
        if not otp_token.startswith("otp-"):
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            otp_id = int(otp_token.split("-")[1])
            otp_obj = PasswordResetOTP.objects.get(id=otp_id, user=user, purpose="password_reset")
        except (ValueError, PasswordResetOTP.DoesNotExist):
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

        # Enforce short window post-verification (e.g., 10 minutes from creation)
        # and ensure it was marked used in Verify step.
        if not otp_obj.used:
            return Response({"error": "OTP not verified"}, status=status.HTTP_400_BAD_REQUEST)

        ttl_after_verify_minutes = 10
        if timezone.now() > otp_obj.created_at + timedelta(minutes=ttl_after_verify_minutes):
            return Response({"error": "Token expired"}, status=status.HTTP_400_BAD_REQUEST)

        # Basic password policy (you can align with front-end policy)
        if len(new_password) < 8:
            return Response({"error": "Password must be at least 8 characters"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)

# class ForgotUsernameOTPAPI(APIView):
#     permission_classes = [permissions.AllowAny]

#     def post(self, request):
#         email = request.data.get("email")
#         if not email:
#             return Response({"error": "Email required"}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             user = User.objects.get(email__iexact=email)
#         except User.DoesNotExist:
#             return Response({"message": "If an account exists, an OTP has been sent."}, status=status.HTTP_200_OK)

#         if not can_issue_otp(user):
#             return Response({"message": "If an account exists, an OTP has been sent."}, status=status.HTTP_200_OK)

#         code = generate_otp()
#         PasswordResetOTP.objects.create(user=user, code=code, purpose="username_recovery")
#         try:
#             subject = "Username Recovery OTP"
#             message = (
#                 f"Hello,\n\nYour OTP code is: {code}\n"
#                 f"It expires in {getattr(settings, 'OTP_TTL_MINUTES', 5)} minutes."
#             )
#             send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
#         except BadHeaderError:
#             return Response({"error": "Invalid email header"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         except Exception:
#             return Response({"error": "Email sending failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         return Response({"message": "If an account exists, an OTP has been sent."}, status=status.HTTP_200_OK)

# class VerifyUsernameOTPAPI(APIView):
#     permission_classes = [permissions.AllowAny]

#     def post(self, request):
#         email = request.data.get("email")
#         otp = request.data.get("otp")
#         if not email or not otp:
#             return Response({"error": "Email and OTP required"}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             user = User.objects.get(email__iexact=email)
#         except User.DoesNotExist:
#             return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             latest = PasswordResetOTP.objects.filter(
#                 user=user, code=otp, purpose="username_recovery", used=False
#             ).latest("created_at")
#         except PasswordResetOTP.DoesNotExist:
#             return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

#         ttl = getattr(settings, "OTP_TTL_MINUTES", 5)
#         if not latest.is_valid(ttl_minutes=ttl):
#             return Response({"error": "OTP expired"}, status=status.HTTP_400_BAD_REQUEST)

#         latest.used = True
#         latest.save()

#         # Do not expose username in API response (to avoid enumeration patterns).
#         # Email the username again upon successful verification for consistency.
#         try:
#             send_mail(
#                 subject="Your Username",
#                 message=f"Hello,\n\nYour username is: {user.username}",
#                 from_email=settings.DEFAULT_FROM_EMAIL,
#                 recipient_list=[user.email],
#                 fail_silently=False,
#             )
#         except Exception:
#             # Still return success to avoid leaking info; log the error in production
#             pass

#         return Response({"message": "Username sent to your email"}, status=status.HTTP_200_OK)