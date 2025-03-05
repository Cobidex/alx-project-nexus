from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import JobDetailViewSet

job_router = DefaultRouter(trailing_slash=False)
job_router.register("details", JobDetailViewSet, basename='job-details')

urlpatterns = [
    path('jobs/', include(job_router.urls)),
]
