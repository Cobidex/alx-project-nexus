from rest_framework import mixins, viewsets, permissions, status
from rest_framework.response import Response
from authentication.serializers import User, UserSerializer

class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin, 
                  viewsets.GenericViewSet): 
    """ViewSet for retrieving, listing, updating, and deleting users."""
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Restrict non-admin users to only their own profile."""
        return self.queryset if self.request.user.is_staff else self.queryset.filter(id=self.request.user.id)

    def check_permissions(self, request, obj):
        """Ensure users can only modify their profile unless they are admins."""
        if not request.user.is_staff and obj.id != request.user.id:
            self.permission_denied(request, message="You can only modify your own profile.")

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        self.check_permissions(request, instance)

        if "password" in request.data:
            return Response({"error": "Updating the password field is not allowed."}, status=status.HTTP_400_BAD_REQUEST)

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.check_permissions(request, instance)
        return super().destroy(request, *args, **kwargs)
