from drf_yasg import openapi
from .serializers import CustomTokenObtainPairSerializer

# ---- Request Password Reset Swagger Docs ----
request_password_reset_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=["email"],
    properties={
        "email": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL)
    }
)

request_password_reset_responses = {
    200: openapi.Response("OTP sent to email"),
    400: openapi.Response("Email is required"),
    404: openapi.Response("User not found"),
}

# ---- Reset Password Swagger Docs ----
reset_password_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=["email", "otp", "new_password"],
    properties={
        "email": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
        "otp": openapi.Schema(type=openapi.TYPE_INTEGER),
        "new_password": openapi.Schema(type=openapi.TYPE_STRING),
    },
)

reset_password_responses = {
    200: openapi.Response("Password reset successful"),
    400: openapi.Response("Invalid or expired OTP"),
    404: openapi.Response("User not found"),
}

# ---- Custom Token Obtain Pair Swagger Docs ----
token_obtain_request_schema = CustomTokenObtainPairSerializer

token_obtain_response_schema = openapi.Response(
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
)

token_obtain_unauthorized_schema = openapi.Response(
    description="Invalid credentials",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "detail": openapi.Schema(type=openapi.TYPE_STRING, description="Error message"),
        },
    ),
)
