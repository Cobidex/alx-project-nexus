from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import JobDetailViewSet, CompanyViewSet, JobViewSet, JobApplicationViewSet

job_router = DefaultRouter(trailing_slash=False)
job_router.register("jobs", JobViewSet, basename="job")
job_router.register("applications", JobApplicationViewSet, basename="application")
job_router.register("company", CompanyViewSet, basename="company")
#job_router.register("jobs/details", JobDetailViewSet, basename='job-details')

urlpatterns = [
    path('', include(job_router.urls)),
]
