from rest_framework import serializers
from .models import JobCategory, Job, JobApplication

# Job Category Serializer
class JobCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = JobCategory
        fields = "__all__"
        ordering = ["-created_at"]

# Job Serializer
class JobSerializer(serializers.ModelSerializer):
    posted_by = serializers.StringRelatedField()

    class Meta:
        model = Job
        fields = ["id", "title", "description", "company", "location", "category", "posted_by"]
        ordering = ["-created_at"]

class JobApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = '__all__'
        ordering = ["-created_at"]
