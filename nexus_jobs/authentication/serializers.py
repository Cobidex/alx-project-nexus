from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from rest_framework import serializers

from jobs.serializers import CompanySerializer
from .models import Role

User = get_user_model()

# Role Serializer
class RoleSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(format='hex_verbose')
    class Meta:
        model = Role
        fields = "__all__"

# User Serializer
class UserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(format='hex_verbose')
    role = RoleSerializer(read_only=True)
    company = CompanySerializer(read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "role", "company"]

# User Registration Serializer
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    role = serializers.CharField()

    class Meta:
        model = User
        fields = ["email", "password", "first_name", "last_name", "role"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        password = validated_data.pop("password")
        role_name = validated_data.pop("role")
        role = None
        try:
            role = Role.objects.get(name=role_name)
        except Role.DoesNotExist:
            raise serializers.ValidationError("Role does not exist")
        user = User.objects.create(**validated_data, role=role)
        user.set_password(password)
        user.save()
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom serializer to return user data along with JWT tokens."""

    def validate(self, attrs):
        data = super().validate(attrs)

        # Get the authenticated user
        user = self.user

        # Add user details to the response
        data.update({
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role.name,
                "company": CompanySerializer(getattr(user, "company", None), context=self.context).data if hasattr(user, "company") else None
            }
        })
        return data

