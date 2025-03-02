from rest_framework import permissions

class IsEmployer(permissions.BasePermission):
    """Only employers can post or edit jobs."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role.name == "Employer"

class IsApplicant(permissions.BasePermission):
    """Only applicants can apply for jobs."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role.name == "Applicant"
    
class IsAdmin(permissions.BasePermission):
    """Only admins can update job catagories."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role.name == "Admin"
    
class IsCompanyOwner(permissions.BasePermission):
    """
    Custom permission to allow only the company owner or an admin to modify a company.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions (GET, HEAD, OPTIONS) are allowed to authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner or an admin
        return obj.posted_by == request.user or request.user.is_staff


class IsJobOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to allow only the job owner or an admin to modify a job.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions (GET, HEAD, OPTIONS) are allowed to authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner or an admin
        return obj.posted_by == request.user or request.user.is_staff