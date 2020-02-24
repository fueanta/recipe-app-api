from rest_framework import viewsets, mixins, authentication, permissions

from core.models import Tag

from recipe import serializers


class TagViewSet(viewsets.GenericViewSet,
                 mixins.ListModelMixin,
                 mixins.CreateModelMixin):
    """Manage tags."""

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    serializer_class = serializers.TagSerializer

    queryset = Tag.objects.all()

    def get_queryset(self):
        """Returns objects specific to the authenticated user."""

        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """Creates tag object."""

        serializer.save(user=self.request.user)
