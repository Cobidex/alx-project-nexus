from rest_framework import serializers
from .models import Company, Job, JobApplication, JobDetail

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = "__all__"
        ordering = ["-created_at"]

class JobDetailSerializer(serializers.ModelSerializer):
    job_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = JobDetail
        fields = ["description", "type", "job_id", "id"]

# Job Serializer
class JobSerializer(serializers.ModelSerializer):
    posted_by = serializers.PrimaryKeyRelatedField(read_only=True)
    company = CompanySerializer(read_only=True)
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
            "experience_level",
            "deadline",
            "location",
            "job_type",
            "posted_by",
            "created_at",
            "details"
        ]
        ordering = ["-created_at"]

class JobApplicationSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(format='hex_verbose')
    job = JobSerializer(read_only=True)
    job_id = serializers.UUIDField(write_only=True)
    status = serializers.ReadOnlyField()
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = JobApplication
        fields = ["id", "user_name", "job", "job_id", "status", "resume", "cover_letter", "applied_at"]
        ordering = ["-created_at"]

    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"