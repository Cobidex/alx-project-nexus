from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q
from authentication.permissions import IsAdmin, IsApplicant, IsEmployer
from rest_framework.permissions import IsAuthenticated
from authentication.models import User
from .services import JobSearchService
from .serializers import CompanySerializer, JobApplicationSerializer, JobCategorySerializer, JobSerializer
from .models import Job, JobApplication, JobCategory, Company

# Create your views here.
class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.select_related("category", "posted_by", "company").all()
    serializer_class = JobSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    def get_permissions(self):
        if self.action in ["create", "update", "destroy"]:
            return [IsAuthenticated(), IsEmployer()]
        return [IsAuthenticated()]

    def list(self, request, *args, **kwargs):
        # Generate a unique cache key based on the request's query params
        query_params = request.query_params.urlencode()  # Get query string (e.g., "page=2&page_size=10")
        cache_key = f"job_list_{urlsafe_base64_encode(force_bytes(query_params))}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=300)
        return response
    
    def perform_create(self, serializer):
        try:
            company = get_object_or_404(Company, user=self.request.user)
        except:
            raise APIException({"error": "You must have a company to post a job."})
        serializer.save(posted_by=self.request.user, company=company)

    @action(detail=False, methods=["get"], url_path="search")
    def search_jobs(self, request):
        """Search for jobs using full-text search and fuzzy search."""
        query = request.query_params.get("q", "").strip()
        job_type = request.query_params.get("job_type", None)
        location = request.query_params.get("location", None)
        min_salary = request.query_params.get("min_salary", None)

        jobs = JobSearchService.search_jobs(query, job_type, location, min_salary)

        # Paginate results
        page = self.paginate_queryset(jobs)
        if page is not None:
            serializer = JobSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = JobSerializer(jobs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=["get"], permission_classes=[IsApplicant])
    def saved_jobs(self, request):
        """Retrieve a list of saved jobs for the authenticated user."""
        saved_jobs = request.user.saved_jobs.all()
        serializer = self.get_serializer(saved_jobs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[IsApplicant])
    def save_job(self, request, pk=None):
        """Allow users to save a job."""
        job = self.get_object()
        user = request.user

        if job in user.saved_jobs.all():
            return Response({"message": "Job is already saved."}, status=400)

        user.saved_jobs.add(job)
        return Response({"message": "Job saved successfully."}, status=200)

    @action(detail=True, methods=["post"], permission_classes=[IsApplicant])
    def remove_saved_job(self, request, pk=None):
        """Allow users to remove a saved job."""
        job = self.get_object()
        user = request.user

        if job not in user.saved_jobs.all():
            return Response({"message": "Job is not in saved jobs."}, status=400)

        user.saved_jobs.remove(job)
        return Response({"message": "Job removed from saved jobs."}, status=200)


class JobApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = JobApplicationSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["job", "user"]
    search_fields = ["job__title"]
    ordering_fields = ["created_at"]

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated(), IsApplicant()]
        return [IsAuthenticated()]

    def list(self, request, *args, **kwargs):
        query_params = request.query_params.urlencode()  # Get query string (e.g., "page=2&page_size=10")
        cache_key = f"job_app_list_{urlsafe_base64_encode(force_bytes(query_params))}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=300)
        return response

    def get_queryset(self):
        if not isinstance(self.request.user, User):
            return JobApplication.objects.none()
        
        return JobApplication.objects.filter(
            Q(user=self.request.user) |  # Applications made by the user
            Q(job__posted_by=self.request.user)  # Applications to jobs posted by the user
        ).select_related("job")

    def update(self, request, *args, **kwargs):
        """Allow only the job owner to update status to 'interview', 'accepted', or 'rejected' but not 'withdrawn'."""
        application = self.get_object()

        if application.job.posted_by != request.user:
            return Response({"error": "Only the job owner can update the application status."}, status=status.HTTP_403_FORBIDDEN)

        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Allow only the applicant to withdraw (delete) their application and remove the resume."""
        application = self.get_object()

        if application.user != request.user:
            return Response({"error": "You can only withdraw your own application."}, status=status.HTTP_403_FORBIDDEN)
        
        application.delete()

        return Response({"message": "Application withdrawn and deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class JobCategoryViewSet(viewsets.ModelViewSet):
    queryset = JobCategory.objects.all()
    serializer_class = JobCategorySerializer

    def get_permissions(self):
        if self.action in ["create", "update", "destroy"]:
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated()]
    
class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

    def get_permissions(self):
        if self.action in ["create", "update", "destroy"]:
            return [IsAuthenticated(), IsEmployer()]
        return [IsAuthenticated()]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
