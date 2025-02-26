from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import JobViewSet, JobApplicationViewSet

job_router = DefaultRouter()
job_router.register("jobs", JobViewSet, basename="job")
job_router.register("applications", JobApplicationViewSet, basename="application")

urlpatterns = [
    path('', include(job_router.urls)),
]
