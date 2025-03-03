from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import CompanyViewSet, JobViewSet, JobApplicationViewSet

job_router = DefaultRouter()
job_router.register("jobs", JobViewSet, basename="job")
job_router.register("applications", JobApplicationViewSet, basename="application")
job_router.register("company", CompanyViewSet, basename="company")

urlpatterns = [
    path('', include(job_router.urls)),
]
