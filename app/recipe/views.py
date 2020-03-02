import logging

from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import Tag, Ingredient, Recipe
from recipe import serializers


def _params_to_ints(qs):
    """Convert a list of string IDs to a list of integers."""

    return [int(str_id) for str_id in qs.split(',')]


class BaseRecipeAttrViewSet(viewsets.GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.CreateModelMixin):
    """Base class for common recipe attribute classes."""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Returns attr objects specific to the authenticated user."""

        assigned_only = bool(self.request.query_params.get('assigned_only'))

        queryset = self.queryset

        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)

        return queryset.filter(user=self.request.user).order_by('-name')

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

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    serializer_class = serializers.RecipeSerializer

    queryset = Recipe.objects.all()

    def get_queryset(self):
        """Retrieve the recipes for the authenticated user"""

        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')

        queryset = self.queryset

        if tags:
            tag_ids = _params_to_ints(tags)

            logging.getLogger('debugger').debug(f'Tag IDs: {tag_ids}')

            queryset = queryset.filter(tags__id__in=tag_ids)

        if ingredients:
            ingredient_ids = _params_to_ints(ingredients)

            logging.getLogger('debugger') \
                .debug(f'Ingredient IDs: {ingredient_ids}')

            queryset = queryset.filter(ingredients__id__in=ingredient_ids)

        return queryset.filter(user=self.request.user).distinct()

    def get_serializer_class(self):
        """Returns appropriate serializer class based on action."""

        if self.action == 'retrieve':
            return serializers.RecipeDetailSerializer
        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Creates recipe object."""

        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to a recipe."""

        recipe = self.get_object()

        serializer = self.get_serializer(
            recipe,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
