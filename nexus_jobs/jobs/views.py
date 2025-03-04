from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework.exceptions import APIException
from rest_framework import mixins, viewsets, permissions
from rest_framework.response import Response
from rest_framework import status
from .serializers import BenefitSerializer
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Q
from authentication.permissions import IsApplicant, IsEmployer
from authentication.models import User
from .services import JobSearchService
from .serializers import CompanySerializer, JobApplicationSerializer, JobSerializer
from .models import Job, Company, JobApplication, Benefit

class JobViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing job listings.
    """
    queryset = Job.objects.select_related("category", "posted_by", "company").all()
    serializer_class = JobSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    def get_permissions(self):
        if self.action in ["create", "update", "destroy"]:
            return [IsAuthenticated(), IsEmployer()]
        return [IsAuthenticated()]

    @swagger_auto_schema(responses={200: JobSerializer(many=True)})
    def list(self, request, *args, **kwargs):
        """
        Retrieve a list of jobs with caching for optimized performance.
        """
        query_params = request.query_params.urlencode()
        cache_key = f"job_list_{urlsafe_base64_encode(force_bytes(query_params))}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=300)
        return response
    
    @swagger_auto_schema(request_body=JobSerializer, responses={201: JobSerializer})
    def perform_create(self, serializer):
        """
        Create a new job posting. Only employers can post jobs.
        """
        try:
            company = get_object_or_404(Company, user=self.request.user)
        except:
            raise APIException({"error": "You must have a company to post a job."})
        serializer.save(posted_by=self.request.user, company=company)
    
    @swagger_auto_schema(
        method="get",
        manual_parameters=[
            openapi.Parameter("q", openapi.IN_QUERY, description="Search query", type=openapi.TYPE_STRING),
            openapi.Parameter("job_type", openapi.IN_QUERY, description="Job type filter", type=openapi.TYPE_STRING),
            openapi.Parameter("location", openapi.IN_QUERY, description="Location filter", type=openapi.TYPE_STRING),
            openapi.Parameter("min_salary", openapi.IN_QUERY, description="Minimum salary filter", type=openapi.TYPE_INTEGER),
            openapi.Parameter("experience_level", openapi.IN_QUERY, description="Experience level filter", type=openapi.TYPE_STRING),
        ],
        responses={200: JobSerializer(many=True)},
    )
    @action(detail=False, methods=["get"], url_path="search")
    def search_jobs(self, request):
        """
        Search for jobs using full-text and fuzzy search with filtering options.
        """
        query = request.query_params.get("q", "").strip()
        job_type = request.query_params.get("job_type")
        location = request.query_params.get("location")
        min_salary = request.query_params.get("min_salary")
        experience_level = request.query_params.get("experience_level")
        
        query_params = request.query_params.urlencode()
        cache_key = f"search_{urlsafe_base64_encode(force_bytes(query_params))}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        jobs = JobSearchService.search_jobs(query, job_type, location, min_salary, experience_level)
        
        page = self.paginate_queryset(jobs)
        if page is not None:
            serializer = JobSerializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            cache.set(cache_key, response, timeout=300)
            return response

        serializer = JobSerializer(jobs, many=True)
        cache.set(cache_key, serializer.data, timeout=300)
        return Response(serializer.data)
    
    @swagger_auto_schema(responses={200: JobSerializer(many=True)})
    @action(detail=False, methods=["get"], permission_classes=[IsApplicant])
    def saved_jobs(self, request):
        """
        Retrieve a list of saved jobs for the authenticated user.
        """
        saved_jobs = request.user.saved_jobs.all()
        serializer = self.get_serializer(saved_jobs, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(responses={200: "Job saved successfully.", 400: "Job is already saved."})
    @action(detail=True, methods=["post"], permission_classes=[IsApplicant])
    def save_job(self, request, pk=None):
        """
        Allow users to save a job.
        """
        job = self.get_object()
        user = request.user

        if job in user.saved_jobs.all():
            return Response({"message": "Job is already saved."}, status=400)

        user.saved_jobs.add(job)
        return Response({"message": "Job saved successfully."}, status=200)

    @swagger_auto_schema(responses={200: "Job removed from saved jobs.", 400: "Job is not in saved jobs."})
    @action(detail=True, methods=["post"], permission_classes=[IsApplicant])
    def remove_saved_job(self, request, pk=None):
        """
        Allow users to remove a saved job.
        """
        job = self.get_object()
        user = request.user

        if job not in user.saved_jobs.all():
            return Response({"message": "Job is not in saved jobs."}, status=400)

        user.saved_jobs.remove(job)
        return Response({"message": "Job removed from saved jobs."}, status=200)


class JobApplicationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling job applications.
    - Applicants can create applications.
    - Employers can view applications for their posted jobs.
    """
    serializer_class = JobApplicationSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["job", "user"]
    search_fields = ["job__title"]
    ordering_fields = ["created_at"]

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated(), IsApplicant()]
        return [IsAuthenticated()]

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('job', openapi.IN_QUERY, description="Filter by job ID", type=openapi.TYPE_INTEGER),
        openapi.Parameter('user', openapi.IN_QUERY, description="Filter by user ID", type=openapi.TYPE_INTEGER)
    ])
    def list(self, request, *args, **kwargs):
        """Retrieve a list of job applications."""
        query_params = request.query_params.urlencode()
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
            Q(user=self.request.user) |
            Q(job__posted_by=self.request.user)
        ).select_related("job")

    def update(self, request, *args, **kwargs):
        """Allow only job owners to update application status."""
        application = self.get_object()
        if application.job.posted_by != request.user:
            return Response({"error": "Only the job owner can update the application status."},
                            status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Allow only applicants to withdraw their applications."""
        application = self.get_object()
        if application.user != request.user:
            return Response({"error": "You can only withdraw your own application."},
                            status=status.HTTP_403_FORBIDDEN)
        application.delete()
        return Response({"message": "Application withdrawn successfully."}, status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CompanyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing companies.
    - Employers can create, update, and delete companies.
    - Users can list and retrieve companies.
    """
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

    def get_permissions(self):
        if self.action in ["create", "update", "destroy"]:
            return [IsAuthenticated(), IsEmployer()]
        return [IsAuthenticated()]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class BenefitViewSet(mixins.CreateModelMixin,
                     mixins.DestroyModelMixin,
                     viewsets.GenericViewSet):
    """
    ViewSet for managing job benefits.
    - Job posters can add or remove benefits.
    """
    queryset = Benefit.objects.all()
    serializer_class = BenefitSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """Ensure only the job poster can add benefits."""
        job_id = serializer.validated_data['job']
        job = Job.objects.get(id=job_id)
        if job.posted_by != self.request.user.id:
            return Response({"error": "You can only add benefits to jobs you posted."},
                            status=status.HTTP_403_FORBIDDEN)
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        """Ensure only the job poster can delete benefits."""
        benefit = self.get_object()
        if benefit.job.posted_by != request.user.id:
            return Response({"error": "You can only delete benefits from jobs you posted."},
                            status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)
