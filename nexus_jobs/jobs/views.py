from rest_framework import viewsets, permissions
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.parsers import MultiPartParser, FormParser
from authentication.permissions import IsAdmin, IsApplicant, IsEmployer
from rest_framework.permissions import IsAuthenticated
from authentication.models import User
from .serializers import JobApplicationSerializer, JobCategorySerializer, JobSerializer
from .models import Job, JobApplication, JobCategory

# Create your views here.
class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.select_related("category", "posted_by").all()
    serializer_class = JobSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["category", "location"]
    search_fields = ["title", "description", "company"]
    ordering_fields = ["created_at"]

    def get_permissions(self):
        if self.action in ["create", "update", "destroy"]:
            return [IsAuthenticated(), IsEmployer()]
        return [permissions.AllowAny()]

    def list(self, request, *args, **kwargs):
        cache_key = "job_list"
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=300)
        return response
    
    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)

class JobApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = JobApplicationSerializer
    permission_classes = [IsAuthenticated, IsApplicant]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["job", "user"]
    search_fields = ["job__title"]
    ordering_fields = ["created_at"]
    parser_classes = (MultiPartParser, FormParser)

    def list(self, request, *args, **kwargs):
        cache_key = "job_application_list"
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=300)
        return response

    def get_queryset(self):
        if not isinstance(self.request.user, User):
            return None
        return JobApplication.objects.filter(user=self.request.user).select_related("job")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class JobCategoryViewSet(viewsets.ModelViewSet):
    queryset = JobCategory.objects.all()
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = JobCategorySerializer

