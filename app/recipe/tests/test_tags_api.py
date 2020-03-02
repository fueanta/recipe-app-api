from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Recipe
from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


def sample_user(email='test@fueanta.com', password='pass123'):
    """Creates and returns sample user object for test."""

    return get_user_model().objects.create_user(email, password)


def sample_tag(name, user):
    """Creates and returns sample tag object for test."""

    return Tag.objects.create(name=name, user=user)


def sample_recipe(user, **params):
    """Creates and returns a sample recipe."""

    defaults = {
        'title': 'Sample recipe',
        'time_in_minutes': 10,
        'price': 5.00,
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


class PublicTagsApiTests(TestCase):
    """Test cases for publicly facing Tags API endpoints."""

    def setUp(self):
        self.client = APIClient()

    def test_login_required_to_retrieve_tags(self):
        """Testing if login is mandatory to retrieve tags."""

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Test Tags API endpoints that require authentication."""

    def setUp(self):
        self.user = sample_user()

        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Testing if authenticated user can retrieve tags."""

        sample_tag(name='Vegan', user=self.user)
        sample_tag(name='Dessert', user=self.user)

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')

        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_retrieval_limited_to_authenticated_user(self):
        """Testing if tags returned is limited to authenticated user only."""

        tag = sample_tag(name='Vegan', user=self.user)

        user2 = sample_user(email='test2@fueanta.com', password='pass123')
        sample_tag(name='Dessert', user=user2)

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_successful_tag_creation(self):
        """Testing if tag created successfully."""

        payload = {"name": 'Dinner'}

        res = self.client.post(TAGS_URL, payload)

        exists = Tag.objects.all().filter(
            name=payload['name'],
            user=self.user,
        ).exists()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(exists)

    def test_invalid_tag_creation_fails(self):
        """Testing if tag creation with invalid payload fails."""

        payload = {"name": ''}

        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_assigned_to_recipes(self):
        """Test filtering tags by those assigned to recipes."""

        tag = sample_tag(name='Breakfast', user=self.user)
        tag2 = sample_tag(name='Lunch', user=self.user)

        recipe = sample_recipe(user=self.user)
        recipe.tags.add(tag)

        res = self.client.get(path=TAGS_URL, data={'assigned_only': 1})

        serializer = TagSerializer(tag)
        serializer2 = TagSerializer(tag2)

        self.assertIn(serializer.data, res.data)
        self.assertNotIn(serializer2.data, res.data)
