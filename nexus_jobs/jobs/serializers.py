from rest_framework import serializers
from .models import Company, JobCategory, Job, JobApplication

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = "__all__"
        ordering = ["-created_at"]

# Job Category Serializer
class JobCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = JobCategory
        fields = "__all__"
        ordering = ["-created_at"]

# Job Serializer
class JobSerializer(serializers.ModelSerializer):
    posted_by = serializers.PrimaryKeyRelatedField(read_only=True)
    company = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Job
        fields = [
            "id",
            "title",
            "description",
            "requirements",
            "company",
            "max_salary",
            "min_salary",
            "status",
            "category",
            "location",
            "job_type",
            "posted_by",
            "created_at",
        ]
        ordering = ["-created_at"]

class JobApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = '__all__'
        ordering = ["-created_at"]
