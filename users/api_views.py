# from django.shortcuts import render

# # Create your views here.
# # -------------------------
# # AUTHENTICATION APIS
# # -------------------------

# # users/api_views.py
# import re
# from django.conf import settings
# from django.core.mail import send_mail, BadHeaderError
# from django.contrib.auth.models import User
# from django.db import transaction
# from django.contrib.auth.tokens import default_token_generator
# from requests import request
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status, permissions
# from .models import Profile
# import uuid
# from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
# from django.utils.encoding import force_bytes, force_str
# import datetime
# from .serializers import UserSerializer
# from django.contrib.auth import get_user_model

# def validate_password_policy(pwd: str) -> bool:
#     # At least 8 chars, one uppercase, one number
#     return bool(re.match(r"^(?=.*[A-Z])(?=.*\d).{8,}$", pwd or ""))

# # def is_valid_phone(phone: str) -> bool:
# #     return bool(re.fullmatch(r"(\+91)?[0-9]{10}", phone or ""))

# User = get_user_model()

# def generate_otp():
#     return f"{random.randint(100000, 999999)}"


# from core.utils.email import send_email

# class RegisterAPI(APIView):
#     permission_classes = [permissions.AllowAny]

#     @transaction.atomic
#     def post(self, request):
#         email = request.data.get("email")
#         password = request.data.get("password")
#         first_name = request.data.get("first_name")
#         last_name = request.data.get("last_name")
#         phone = request.data.get("phone")

#         if not email:
#             return Response({"error": "Email required"}, status=status.HTTP_400_BAD_REQUEST)

#         email = email.lower().strip()
#         existing = User.objects.filter(email__iexact=email).first()

#         # Case 1: Existing user
#         if existing:
#             if existing.is_active:
#                 return Response({"error": "Email already registered"}, status=status.HTTP_400_BAD_REQUEST)
#             else:
#                 # Resend OTP for inactive user
#                 code = generate_otp()
#                 PasswordResetOTP.objects.create(user=existing, code=code, purpose="registration")

#                 subject = "Verify your account"
#                 message = (
#                     f"Hello {existing.first_name or ''},\n\n"
#                     f"Your OTP code is: {code}\n"
#                     f"This code expires in {getattr(settings, 'OTP_TTL_MINUTES', 5)} minutes.\n\n"
#                     f"Enter this code in the app to activate your account."
#                 )
#                 # send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [existing.email])
#                 send_email(existing.email, subject, message)
#                 return Response({"message": "OTP re-sent to email."}, status=status.HTTP_200_OK)

#         # Case 2: New user registration
#         if not password or not first_name or not last_name or not phone:
#             return Response(
#                 {"error": "All fields required for new registration"},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         if Profile.objects.filter(phone=phone).exists():
#             return Response({"error": "Phone already registered"}, status=status.HTTP_400_BAD_REQUEST)

#         auto_username = f"user_{uuid.uuid4().hex[:10]}"

#         user = User.objects.create_user(
#             username=auto_username,
#             email=email,
#             password=password,
#             first_name=first_name.strip(),
#             last_name=last_name.strip(),
#             is_active=False,
#         )
#         user.profile.phone = phone.strip()
#         user.profile.save()

#         code = generate_otp()
#         PasswordResetOTP.objects.create(user=user, code=code, purpose="registration")

#         subject = "Verify your account"
#         message = (
#             f"Hello {first_name},\n\n"
#             f"Your OTP code is: {code}\n"
#             f"This code expires in {getattr(settings, 'OTP_TTL_MINUTES', 5)} minutes.\n\n"
#             f"Enter this code in the app to activate your account."
#         )
#         # send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
#         send_email(user.email, subject, message)
#         return Response({"message": "User created. OTP sent to email."}, status=status.HTTP_201_CREATED)

    
# class VerifyRegistrationOTPAPI(APIView):
#     permission_classes = [permissions.AllowAny]

#     def post(self, request):
#         email = request.data.get("email")
#         otp = request.data.get("otp")

#         if not email or not otp:
#             return Response({"error": "Email and OTP required"}, status=400)

#         try:
#             user = User.objects.get(email__iexact=email)
#         except User.DoesNotExist:
#             return Response({"error": "Invalid email"}, status=400)

#         try:
#             otp_obj = PasswordResetOTP.objects.filter(
#                 user=user, code=otp, purpose="registration", used=False
#             ).latest("created_at")
#         except PasswordResetOTP.DoesNotExist:
#             return Response({"error": "Invalid OTP"}, status=400)

#         ttl = getattr(settings, "OTP_TTL_MINUTES", 5)
#         if not otp_obj.is_valid(ttl_minutes=ttl):
#             return Response({"error": "OTP expired"}, status=400)

#         # Mark OTP as used
#         otp_obj.used = True
#         otp_obj.save()

#         # Activate user
#         user.is_active = True
#         user.save()

#         return Response({"message": "Account verified successfully. You can now log in."}, status=200)

# # users/api_views.py
# from django.contrib.auth import authenticate
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status, permissions
# from rest_framework.authtoken.models import Token
# from django.contrib.auth.models import User
# from .models import Profile

# #login using JWT
# from rest_framework_simplejwt.tokens import RefreshToken
# class LoginAPI(APIView):
#     permission_classes = [permissions.AllowAny]

#     def post(self, request):
#         email = request.data.get("email")
#         phone = request.data.get("phone")
#         password = request.data.get("password")

#         if not password or (not email and not phone):
#             return Response({"error": "Email/Phone and password required"}, status=status.HTTP_400_BAD_REQUEST)

#         user = None
#         if email:
#             user = User.objects.filter(email__iexact=email).first()
#         elif phone:
#             profile = Profile.objects.filter(phone=phone).first()
#             if profile:
#                 user = profile.user

#         if not user:
#             return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

#         user = authenticate(username=user.username, password=password)
#         if not user:
#             return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
#         if not user.is_active:
#             return Response({"error": "Account not activated"}, status=status.HTTP_403_FORBIDDEN)

#         # Return token
#         refresh = RefreshToken.for_user(user)
#         access = str(refresh.access_token)
#         return Response({
#             "message": "Login successful",
#             "access": access,
#             "refresh": str(refresh),
#             "user": {
#                 "id": user.id,
#                 "first_name": user.first_name,
#                 "last_name": user.last_name,
#                 "email": user.email,
#                 "phone": user.profile.phone,
#                 "user": UserSerializer(user).data,
#             }
#         })


# # users/api_views.py
# import random
# from django.conf import settings
# from django.core.mail import send_mail, BadHeaderError
# from django.utils import timezone
# from datetime import timedelta

# from django.contrib.auth.models import User
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status, permissions

# from .models import PasswordResetOTP

# #after user created
# #otp api's for forgot password recovery.
# def generate_otp():
#     return f"{random.randint(100000, 999999)}"

# def can_issue_otp(user):
#     one_hour_ago = timezone.now() - timedelta(hours=1)
#     count = PasswordResetOTP.objects.filter(user=user, created_at__gte=one_hour_ago).count()
#     return count < getattr(settings, "OTP_MAX_PER_HOUR", 5)

# def send_otp_email(user, code, subject_prefix="Password"):
#     subject = f"{subject_prefix} Reset OTP"
#     message = (
#         f"Hello {user.first_name},\n\n"
#         f"Your OTP code is: {code}\n"
#         f"This code expires in {getattr(settings, 'OTP_TTL_MINUTES', 5)} minutes.\n\n"
#         f"If you didn't request this, you can ignore this email."
#     )
#     # send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
#     send_email(user.email, subject, message)
    
# class RequestOTPAPI(APIView):
#     permission_classes = [permissions.AllowAny]

#     def post(self, request):
#         email = request.data.get("email")
#         if not email:
#             return Response({"error": "Email required"}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             user = User.objects.get(email__iexact=email)
#         except User.DoesNotExist:
#             # Do not reveal existence
#             return Response({"message": "If an account exists, an OTP has been sent."}, status=status.HTTP_200_OK)

#         if not can_issue_otp(user):
#             # Avoid enumeration; keep generic response
#             return Response({"message": "If an account exists, an OTP has been sent."}, status=status.HTTP_200_OK)

#         code = generate_otp()
#         PasswordResetOTP.objects.create(user=user, code=code, purpose="password_reset")
#         try:
#             send_otp_email(user, code, subject_prefix="Password")
#         except BadHeaderError:
#             return Response({"error": "Invalid email header"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         except Exception:
#             # Log exception in real apps
#             return Response({"error": "Email sending failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         return Response({"message": "If an account exists, an OTP has been sent."}, status=status.HTTP_200_OK)

# from .utils import generate_temp_token

# class VerifyOTPAPI(APIView):
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
#                 user=user, code=otp, purpose="password_reset", used=False
#             ).latest("created_at")
#         except PasswordResetOTP.DoesNotExist:
#             return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

#         ttl = getattr(settings, "OTP_TTL_MINUTES", 5)
#         if not latest.is_valid(ttl_minutes=ttl):
#             return Response({"error": "OTP expired"}, status=status.HTTP_400_BAD_REQUEST)

#         # ✅ Don’t mark as used yet — only after reset succeeds
#         temp_token = generate_temp_token(latest.id, ttl_minutes=10)
#         return Response({"message": "OTP verified", "otp_token": temp_token}, status=status.HTTP_200_OK)

# from .utils import verify_temp_token
# from datetime import timedelta
# from django.utils import timezone

# class ResetPasswordAPI(APIView):
#     permission_classes = [permissions.AllowAny]

#     def post(self, request):
#         email = request.data.get("email")
#         new_password = request.data.get("new_password")
#         temp_token = request.data.get("otp_token")

#         if not email or not new_password or not temp_token:
#             return Response({"error": "Email, new_password, and otp_token required"}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             user = User.objects.get(email__iexact=email)
#         except User.DoesNotExist:
#             return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)

#         otp_id = verify_temp_token(temp_token, ttl_minutes=10)
#         if not otp_id:
#             return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             otp_obj = PasswordResetOTP.objects.get(id=otp_id, user=user, purpose="password_reset", used=False)
#         except PasswordResetOTP.DoesNotExist:
#             return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

#         # ✅ Reset password
#         if len(new_password) < 8:
#             return Response({"error": "Password must be at least 8 characters"}, status=status.HTTP_400_BAD_REQUEST)

#         user.set_password(new_password)
#         user.save()

#         # Mark OTP as used only after success
#         otp_obj.used = True
#         otp_obj.save()

#         return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)



# from rest_framework.permissions import IsAuthenticated
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from .serializers import ProfileUpdateSerializer, ProfileMeSerializer


# class ProfileUpdateView(APIView):
#     permission_classes = [IsAuthenticated]

#     def put(self, request):
#         profile = request.user.profile
#         user = request.user

#         # If email is included, update it here
#         new_email = request.data.get("email")
#         if new_email:
#             user.email = new_email
#             user.save()

#         serializer = ProfileUpdateSerializer(profile, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({
#                 "first_name": user.first_name,
#                 "last_name": user.last_name,
#                 "email": user.email,
#                 "phone": profile.phone,
#             })

#         return Response(serializer.errors, status=400)



# class ProfileMeView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         serializer = ProfileMeSerializer(request.user.profile)
#         return Response(serializer.data)
    
# class ChangePasswordView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         user = request.user
#         current = request.data.get("current_password")
#         new = request.data.get("new_password")

#         if not user.check_password(current):
#             return Response({"error": "Current password is incorrect"}, status=400)

#         user.set_password(new)
#         user.save()

#         return Response({"message": "Password updated"})

# class RequestEmailChangeView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         new_email = request.data.get("email")

#         if not new_email:
#             return Response({"error": "Email required"}, status=400)

#         if User.objects.filter(email__iexact=new_email).exists():
#             return Response({"error": "Email already in use"}, status=400)

#         code = generate_otp()

#         PasswordResetOTP.objects.create(
#             user=request.user,
#             code=code,
#             purpose="email_change"
#         )

#         send_otp_email(
#             user=request.user,
#             code=code,
#             subject_prefix="Email Change Verification",
#             to_email=new_email
#         )

#         return Response({"message": "OTP sent to new email"})

# class ConfirmEmailChangeView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         otp_code = request.data.get("otp")
#         new_email = request.data.get("email")

#         otp = PasswordResetOTP.objects.filter(
#             user=request.user,
#             code=otp_code,
#             purpose="email_change",
#             used=False
#         ).last()

#         if not otp or not otp.is_valid():
#             return Response({"error": "Invalid or expired OTP"}, status=400)

#         otp.used = True
#         otp.save()

#         # Update email
#         user = request.user
#         user.email = new_email
#         user.save()

#         return Response({"message": "Email updated successfully"})


#test

import random
import uuid
import re
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.core.mail import send_mail, BadHeaderError
from django.db import transaction
from django.utils import timezone

from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from rest_framework_simplejwt.tokens import RefreshToken

from .models import Profile, PasswordResetOTP
from .serializers import (
    ProfileUpdateSerializer,
    ProfileMeSerializer,
    UserSerializer,
)
from core.utils.email import send_email
from .utils import generate_temp_token, verify_temp_token

User = get_user_model()

# ---------------------------------------------------------
# Utility Functions
# ---------------------------------------------------------

def validate_password_policy(pwd: str) -> bool:
    return bool(re.match(r"^(?=.*[A-Z])(?=.*\d).{8,}$", pwd or ""))

def generate_otp():
    return f"{random.randint(100000, 999999)}"

def can_issue_otp(user):
    one_hour_ago = timezone.now() - timedelta(hours=1)
    count = PasswordResetOTP.objects.filter(
        user=user, created_at__gte=one_hour_ago
    ).count()
    return count < getattr(settings, "OTP_MAX_PER_HOUR", 5)

# ⭐ FIXED: Now supports sending to ANY email
def send_otp_email(user, code, subject_prefix="Verification", to_email=None):
    subject = f"{subject_prefix} OTP"
    message = (
        f"Hello {user.first_name},\n\n"
        f"Your OTP code is: {code}\n"
        f"This code expires in {getattr(settings, 'OTP_TTL_MINUTES', 5)} minutes.\n\n"
        f"If you didn't request this, ignore this email."
    )

    recipient = to_email if to_email else user.email
    send_email(recipient, subject, message)

# ---------------------------------------------------------
# Registration
# ---------------------------------------------------------

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
            return Response({"error": "Email required"}, status=400)

        email = email.lower().strip()
        existing = User.objects.filter(email__iexact=email).first()

        # Existing inactive user → resend OTP
        if existing:
            if existing.is_active:
                return Response({"error": "Email already registered"}, status=400)

            code = generate_otp()
            PasswordResetOTP.objects.create(
                user=existing, code=code, purpose="registration"
            )

            send_otp_email(existing, code, "Account Verification")
            return Response({"message": "OTP re-sent to email."}, status=200)

        # New user
        if not password or not first_name or not last_name or not phone:
            return Response({"error": "All fields required"}, status=400)

        if Profile.objects.filter(phone=phone).exists():
            return Response({"error": "Phone already registered"}, status=400)

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

        send_otp_email(user, code, "Account Verification")
        return Response({"message": "User created. OTP sent."}, status=201)

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

        otp_obj.used = True
        otp_obj.save()

        user.is_active = True
        user.save()

        return Response({"message": "Account verified"}, status=200)

# ---------------------------------------------------------
# Login
# ---------------------------------------------------------

class LoginAPI(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        phone = request.data.get("phone")
        password = request.data.get("password")

        if not password or (not email and not phone):
            return Response({"error": "Email/Phone and password required"}, status=400)

        user = None
        if email:
            user = User.objects.filter(email__iexact=email).first()
        elif phone:
            profile = Profile.objects.filter(phone=phone).first()
            if profile:
                user = profile.user

        if not user:
            return Response({"error": "Invalid credentials"}, status=400)

        user = authenticate(username=user.username, password=password)
        if not user:
            return Response({"error": "Invalid credentials"}, status=400)

        if not user.is_active:
            return Response({"error": "Account not activated"}, status=403)

        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "Login successful",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserSerializer(user).data,
        })

# ---------------------------------------------------------
# Forgot Password
# ---------------------------------------------------------

class RequestOTPAPI(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email required"}, status=400)

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response({"message": "If account exists, OTP sent."}, status=200)

        if not can_issue_otp(user):
            return Response({"message": "If account exists, OTP sent."}, status=200)

        code = generate_otp()
        PasswordResetOTP.objects.create(user=user, code=code, purpose="password_reset")

        try:
            send_otp_email(user, code, "Password Reset")
        except Exception:
            return Response({"error": "Email sending failed"}, status=500)

        return Response({"message": "If account exists, OTP sent."}, status=200)

class VerifyOTPAPI(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")

        if not email or not otp:
            return Response({"error": "Email and OTP required"}, status=400)

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response({"error": "Invalid OTP"}, status=400)

        try:
            latest = PasswordResetOTP.objects.filter(
                user=user, code=otp, purpose="password_reset", used=False
            ).latest("created_at")
        except PasswordResetOTP.DoesNotExist:
            return Response({"error": "Invalid OTP"}, status=400)

        ttl = getattr(settings, "OTP_TTL_MINUTES", 5)
        if not latest.is_valid(ttl_minutes=ttl):
            return Response({"error": "OTP expired"}, status=400)

        temp_token = generate_temp_token(latest.id, ttl_minutes=10)
        return Response({"otp_token": temp_token}, status=200)

class ResetPasswordAPI(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        new_password = request.data.get("new_password")
        temp_token = request.data.get("otp_token")

        if not email or not new_password or not temp_token:
            return Response({"error": "Missing fields"}, status=400)

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response({"error": "Invalid request"}, status=400)

        otp_id = verify_temp_token(temp_token, ttl_minutes=10)
        if not otp_id:
            return Response({"error": "Invalid or expired token"}, status=400)

        otp_obj = PasswordResetOTP.objects.filter(
            id=otp_id, user=user, purpose="password_reset", used=False
        ).first()

        if not otp_obj:
            return Response({"error": "Invalid token"}, status=400)

        if len(new_password) < 8:
            return Response({"error": "Password too short"}, status=400)

        user.set_password(new_password)
        user.save()

        otp_obj.used = True
        otp_obj.save()

        return Response({"message": "Password reset successful"}, status=200)

# ---------------------------------------------------------
# Profile
# ---------------------------------------------------------

class ProfileMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = ProfileMeSerializer(request.user.profile)
        return Response(serializer.data)

class ProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        profile = request.user.profile
        serializer = ProfileUpdateSerializer(profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
                "email": request.user.email,
                "phone": profile.phone,
            })

        return Response(serializer.errors, status=400)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        current = request.data.get("current_password")
        new = request.data.get("new_password")

        if not user.check_password(current):
            return Response({"error": "Current password incorrect"}, status=400)

        user.set_password(new)
        user.save()

        return Response({"message": "Password updated"})

# ---------------------------------------------------------
# Email Change OTP
# ---------------------------------------------------------

class RequestEmailChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        new_email = request.data.get("email")

        if not new_email:
            return Response({"error": "Email required"}, status=400)

        if User.objects.filter(email__iexact=new_email).exists():
            return Response({"error": "Email already in use"}, status=400)

        code = generate_otp()

        PasswordResetOTP.objects.create(
            user=request.user,
            code=code,
            purpose="email_change"
        )

        send_otp_email(
            user=request.user,
            code=code,
            subject_prefix="Email Change Verification",
            to_email=new_email
        )

        return Response({"message": "OTP sent to new email"})

class ConfirmEmailChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        otp_code = request.data.get("otp")
        new_email = request.data.get("email")

        otp = PasswordResetOTP.objects.filter(
            user=request.user,
            code=otp_code,
            purpose="email_change",
            used=False
        ).last()

        if not otp or not otp.is_valid():
            return Response({"error": "Invalid or expired OTP"}, status=400)

        otp.used = True
        otp.save()

        user = request.user
        user.email = new_email
        user.save()

        return Response({"message": "Email updated successfully"})
