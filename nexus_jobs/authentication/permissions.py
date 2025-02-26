from rest_framework import permissions

class IsEmployer(permissions.BasePermission):
    """Only employers can post or edit jobs."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role.name == "Employer"

class IsApplicant(permissions.BasePermission):
    """Only applicants can apply for jobs."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role.name == "Applicant"
