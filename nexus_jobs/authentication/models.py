import uuid
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _

# Custom User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, role=None, **extra_fields):
        if not email:
            raise ValueError(_("The Email field must be set"))
        
        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)

        updated_role = None
        if role:
            updated_role = Role.objects.filter(name=role).first()
            if not updated_role:
                raise ValueError(_("Invalid role name provided."))

        user = self.model(email=email, role=updated_role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, role=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, role, **extra_fields)

# Role Model
class Role(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

# Custom User Model
class User(AbstractUser):
    username = None  # Remove default username field
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    saved_jobs = models.ManyToManyField("jobs.Job", related_name="saved_by", blank=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()
