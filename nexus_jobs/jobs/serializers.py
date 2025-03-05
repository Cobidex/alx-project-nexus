from rest_framework import serializers
from .models import Company, Job, JobApplication, JobDetail

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = "__all__"
        ordering = ["-created_at"]

class JobDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobDetail
        fields = ["description", "type"]

# Job Serializer
class JobSerializer(serializers.ModelSerializer):
    posted_by = serializers.PrimaryKeyRelatedField(read_only=True)
    company = serializers.PrimaryKeyRelatedField(read_only=True)
    details = JobDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Job
        fields = [
            "id",
            "title",
            "description",
            "company",
            "max_salary",
            "min_salary",
            "is_active",
            "category",
            "location",
            "job_type",
            "posted_by",
            "created_at",
            "details"
        ]
        ordering = ["-created_at"]

class JobApplicationSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    status = serializers.ReadOnlyField()

    class Meta:
        model = JobApplication
        fields = '__all__'
        ordering = ["-created_at"]
