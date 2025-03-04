from rest_framework import generics, permissions
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import CustomTokenObtainPairSerializer, RegisterSerializer
from .models import User
import random
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

class RegisterView(generics.CreateAPIView):
    """
    Register a new user.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class RequestPasswordResetView(APIView):
    """
    Generates an OTP and sends it to the user's email for password reset.
    """

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL)
            }
        ),
        responses={
            200: openapi.Response("OTP sent to email"),
            400: openapi.Response("Email is required"),
            404: openapi.Response("User not found")
        }
    )
    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        otp = random.randint(100000, 999999)
        cache.set(f"password_reset_otp_{email}", otp, timeout=300)

        send_mail(
            subject="Password Reset OTP",
            message=f"Your password reset OTP is {otp}. It will expire in 5 minutes.",
            from_email="no-reply@example.com",
            recipient_list=[email],
        )

        return Response({"message": "OTP sent to email"}, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    """
    Allows a user to reset their password after verifying the OTP.
    """

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'otp', 'new_password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
                'otp': openapi.Schema(type=openapi.TYPE_INTEGER),
                'new_password': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        responses={
            200: openapi.Response("Password reset successful"),
            400: openapi.Response("Invalid or expired OTP"),
            404: openapi.Response("User not found")
        }
    )
    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")
        new_password = request.data.get("new_password")

        if not email or not otp or not new_password:
            return Response({"error": "Email, OTP, and new password are required"}, status=status.HTTP_400_BAD_REQUEST)

        cached_otp = cache.get(f"password_reset_otp_{email}")
        if cached_otp and str(cached_otp) == str(otp):
            try:
                user = User.objects.get(email=email)
                user.password = make_password(new_password)
                user.save()
                cache.delete(f"password_reset_otp_{email}")
                return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)



class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT login view that returns user details along with access and refresh tokens.
    """
    serializer_class = CustomTokenObtainPairSerializer

    @swagger_auto_schema(
        request_body=CustomTokenObtainPairSerializer,
        responses={
            200: openapi.Response(
                description="Successful Login",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "access": openapi.Schema(type=openapi.TYPE_STRING, description="JWT access token"),
                        "refresh": openapi.Schema(type=openapi.TYPE_STRING, description="JWT refresh token"),
                        "user": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_STRING, format="uuid", description="User UUID"),
                                "email": openapi.Schema(type=openapi.TYPE_STRING, format="email", description="User email"),
                                "first_name": openapi.Schema(type=openapi.TYPE_STRING, description="User first name"),
                                "last_name": openapi.Schema(type=openapi.TYPE_STRING, description="User last name"),
                                "role": openapi.Schema(type=openapi.TYPE_STRING, description="User role"),
                            },
                        ),
                    },
                ),
            ),
            401: openapi.Response(
                description="Invalid credentials",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "detail": openapi.Schema(type=openapi.TYPE_STRING, description="Error message"),
                    },
                ),
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)