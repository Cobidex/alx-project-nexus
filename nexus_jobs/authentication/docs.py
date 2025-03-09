from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from .serializers import CustomTokenObtainPairSerializer

register_request_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=["email", "password", "first_name", "last_name", "role"],
    properties={
        "email": openapi.Schema(type=openapi.TYPE_STRING, format="email", example="user@example.com"),
        "password": openapi.Schema(type=openapi.TYPE_STRING, format="password", example="SecurePassword123"),
        "first_name": openapi.Schema(type=openapi.TYPE_STRING, example="John"),
        "last_name": openapi.Schema(type=openapi.TYPE_STRING, example="Doe"),
        "role": openapi.Schema(
            type=openapi.TYPE_STRING,
            enum=["Applicant", "Employer"],
            example="Applicant",
            description="Role must be either 'Applicant' or 'Employer'."
        ),
    },
)

register_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "status": openapi.Schema(type=openapi.TYPE_STRING, example="success"),
        "data": openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING, example="user@example.com"),
                "first_name": openapi.Schema(type=openapi.TYPE_STRING, example="John"),
                "last_name": openapi.Schema(type=openapi.TYPE_STRING, example="Doe"),
                "role": openapi.Schema(type=openapi.TYPE_STRING, example="Applicant"),
            },
        ),
    },
)

register_error_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "status": openapi.Schema(type=openapi.TYPE_STRING, example="error"),
        "message": openapi.Schema(type=openapi.TYPE_STRING, example="Invalid data"),
        "errors": openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING), example=["This field is required."]),
                "role": openapi.Schema(type=openapi.TYPE_STRING, example="Role must be 'Applicant' or 'Employer'."),
            },
        ),
    },
)

register_view_docs = swagger_auto_schema(
    operation_summary="Register a new user",
    operation_description="This endpoint registers a new user with an `Applicant` or `Employer` role.",
    request_body=register_request_schema,
    responses={
        201: openapi.Response("User registered successfully", register_response_schema),
        400: openapi.Response("Validation error", register_error_schema),
    }
)

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
