from rest_framework import serializers
from .models import Benefit, Company, Job, JobApplication

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = "__all__"
        ordering = ["-created_at"]

class BenefitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Benefit
        fields = ["description"]

# Job Serializer
class JobSerializer(serializers.ModelSerializer):
    posted_by = serializers.PrimaryKeyRelatedField(read_only=True)
    company = serializers.PrimaryKeyRelatedField(read_only=True)
    benefits = BenefitSerializer(many=True, read_only=True)

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
            "is_active",
            "category",
            "location",
            "job_type",
            "posted_by",
            "created_at",
            "benefits"
        ]
        ordering = ["-created_at"]

class JobApplicationSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    status = serializers.ReadOnlyField()

    class Meta:
        model = JobApplication
        fields = '__all__'
        ordering = ["-created_at"]
