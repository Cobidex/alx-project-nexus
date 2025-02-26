from rest_framework import serializers
from .models import JobCategory, Job, JobApplication

# Job Category Serializer
class JobCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = JobCategory
        fields = "__all__"

# Job Serializer
class JobSerializer(serializers.ModelSerializer):
    category = JobCategorySerializer(read_only=True)
    posted_by = serializers.StringRelatedField()  # Display user's email instead of ID

    class Meta:
        model = Job
        fields = ["id", "title", "description", "company", "location", "category", "posted_by"]

class JobApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = '__all__'
