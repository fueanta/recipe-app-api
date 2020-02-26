from rest_framework import viewsets, mixins, authentication, permissions

from core.models import Tag, Ingredient, Recipe

from recipe import serializers


class BaseRecipeAttrViewSet(viewsets.GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.CreateModelMixin):
    """Base class for common recipe attribute classes."""

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        """Returns attr objects specific to the authenticated user."""

        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """Creates recipe attr object."""

        serializer.save(user=self.request.user)


class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags."""

    serializer_class = serializers.TagSerializer

    queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingredients."""

    serializer_class = serializers.IngredientSerializer

    queryset = Ingredient.objects.all()


class RecipeViewSet(viewsets.ModelViewSet):
    """Manage recipes."""

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    serializer_class = serializers.RecipeSerializer

    queryset = Recipe.objects.all()

    def get_queryset(self):
        """Returns list of recipes specific to the authenticated user."""

        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Returns appropriate serializer class based on action."""

        if self.action == 'retrieve':
            return serializers.RecipeDetailSerializer

        return self.serializer_class
