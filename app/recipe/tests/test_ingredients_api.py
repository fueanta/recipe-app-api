from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient
from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')


def sample_user(email='test@fueanta.com', password='pass123'):
    """Creates and returns sample user object for test."""

    return get_user_model().objects.create_user(email, password)


def sample_ingredient(name, user):
    """Creates and returns sample ingredient object for test."""

    return Ingredient.objects.create(name=name, user=user)


class PublicIngredientsApiTests(TestCase):
    """Test cases for publicly facing Ingredients API endpoints."""

    def setUp(self):
        self.client = APIClient()

    def test_login_required_to_retrieve_ingredients(self):
        """Testing if login is mandatory to retrieve ingredients."""

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """Test cases for Ingredient API endpoints that require authentication."""

    def setUp(self):
        self.user = sample_user()

        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_successful_retrieval_of_ingredients(self):
        """Testing if user can retrieve ingredients after authentication."""

        sample_ingredient(name='Sugar', user=self.user)
        sample_ingredient(name='Salt', user=self.user)

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')

        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_retrieval_limited_to_authenticated_user(self):
        """
        Testing if ingredients returned is limited to authenticated user only.
        """

        ingredient = sample_ingredient(name='Coconut', user=self.user)

        user2 = sample_user(email='test2@fueanta.com', password='pass123')
        sample_ingredient(name='Onion', user=user2)

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_successful_ingredient_creation(self):
        """Testing if ingredient created successfully."""

        payload = {"name": 'Garlic'}

        res = self.client.post(INGREDIENTS_URL, payload)

        exists = Ingredient.objects.all().filter(
            name=payload['name'],
            user=self.user,
        ).exists()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(exists)

    def test_invalid_ingredient_creation_fails(self):
        """Testing if ingredient creation with invalid payload fails."""

        payload = {"name": ''}

        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
