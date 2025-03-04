from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import CustomTokenObtainPairView, RegisterView, RequestPasswordResetView, ResetPasswordView

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/password-reset/request/", RequestPasswordResetView.as_view(), name="request_password_reset"),
    path("auth/password-reset/reset/", ResetPasswordView.as_view(), name="reset_password"),
]