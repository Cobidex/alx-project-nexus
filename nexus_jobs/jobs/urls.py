from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import BenefitViewSet, CompanyViewSet, JobViewSet, JobApplicationViewSet

job_router = DefaultRouter()
job_router.register("jobs", JobViewSet, basename="job")
job_router.register("applications", JobApplicationViewSet, basename="application")
job_router.register("company", CompanyViewSet, basename="company")
job_router.register(r'jobs/benefits', BenefitViewSet, basename='benefit')

urlpatterns = [
    path('', include(job_router.urls)),
]
