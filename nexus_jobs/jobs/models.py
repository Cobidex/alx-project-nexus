import uuid
from django.db import models
from django.contrib.postgres.search import SearchVectorField
from django.db.models import F
from django.contrib.postgres.indexes import GinIndex
from authentication.models import User

# Job Category
class JobCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Company(models.Model):
     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
     name = models.CharField(max_length=255)
     user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, editable=False)

     def __str__(self):
          return super().__str__()


class Job(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    requirements = models.TextField()
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    max_salary = models.IntegerField()
    min_salary = models.IntegerField()
    is_active = models.BooleanField(default=True)
    category = models.ForeignKey("JobCategory", on_delete=models.CASCADE, null=False)
    location = models.CharField(max_length=100)
    job_type = models.CharField(
        max_length=50, choices=[("Full-time", "Full-time"), ("Part-time", "Part-time")]
    )
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, null=False, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    search_vector = SearchVectorField(null=True)

    class Meta:
        indexes = [
            GinIndex(fields=["search_vector"], name="search_vector_gin"),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class JobApplication(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("interview", "Interview"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    resume = models.CharField(max_length=255)
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} applied for {self.job.title}"