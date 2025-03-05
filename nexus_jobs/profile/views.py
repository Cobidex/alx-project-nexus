from rest_framework import mixins, viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
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

    def check_permissions(self, request, obj=None):
        """Ensure users can only modify their profile unless they are admins."""
        if obj is not None and not request.user.is_staff and obj.id != request.user.id:
            self.permission_denied(request, message="You can only modify your own profile.")


    @swagger_auto_schema(
        method='get',
        operation_description="Retrieve the profile of the authenticated user.",
        responses={200: UserSerializer}
    )
    @action(detail=False, methods=['get'], url_path='me', permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """Returns the profile of the authenticated user."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Update a user's profile. Password updates are not allowed.",
        request_body=UserSerializer,
        responses={200: UserSerializer, 400: "Updating the password field is not allowed."}
    )
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        self.check_permissions(request, instance)

        if "password" in request.data:
            return Response({"error": "Updating the password field is not allowed."}, status=status.HTTP_400_BAD_REQUEST)

        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Delete a user profile. Users can only delete their own profile unless they are admins.",
        responses={204: "Profile deleted successfully."}
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.check_permissions(request, instance)
        return super().destroy(request, *args, **kwargs)
