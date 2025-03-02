from rest_framework import generics, permissions
from .models import User
import random
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from django.core.cache import cache
from .serializers import RegisterSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class RequestPasswordResetView(APIView):
    """Generates OTP and sends it to the user's email"""

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if user exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Generate OTP
        otp = random.randint(100000, 999999)
        cache.set(f"password_reset_otp_{email}", otp, timeout=300)

        # Send OTP via email
        send_mail(
            subject="Password Reset OTP",
            message=f"Your password reset OTP is {otp}. It will expire in 5 minutes.",
            from_email="no-reply@example.com",
            recipient_list=[email],
        )

        return Response({"message": "OTP sent to email"}, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    """Allows user to reset password after verifying OTP"""

    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")
        new_password = request.data.get("new_password")

        if not email or not otp or not new_password:
            return Response({"error": "Email, OTP, and new password are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate OTP
        cached_otp = cache.get(f"password_reset_otp_{email}")
        if cached_otp and str(cached_otp) == str(otp):
            try:
                user = User.objects.get(email=email)
                user.password = make_password(new_password)
                user.save()

                # Delete OTP from cache after successful reset
                cache.delete(f"password_reset_otp_{email}")

                return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)