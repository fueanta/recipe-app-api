from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Returns recipe detail URL."""

    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_user(email='test@fueanta.com', password='pass123'):
    """Creates and returns sample user object for test."""

    return get_user_model().objects.create_user(email, password)


def sample_tag(user, name='Vegan'):
    """Creates and returns sample tag object for test."""

    return Tag.objects.create(name=name, user=user)


def sample_ingredient(user, name='Coconut'):
    """Creates and returns sample ingredient object for test."""

    return Ingredient.objects.create(name=name, user=user)


def sample_recipe(user, **params):
    """Creates and returns a sample recipe."""

    defaults = {
        'title': 'Sample recipe',
        'time_in_minutes': 10,
        'price': 5.00,
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTests(TestCase):
    """Test unauthenticated recipe API access."""

    def setUp(self):
        self.client = APIClient()

    def test_required_auth(self):
        """Test the authenticaiton is required"""

        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test authenticated recipe API access"""

    def setUp(self):
        self.user = sample_user()

        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving list of recipes"""

        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')

        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """Test retrieving recipes for user"""

        sample_recipe(user=self.user)

        user2 = sample_user(email='test2@fueanta.com', password='pass123')
        sample_recipe(user=user2)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)

        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_successful_recipe_detail_retrieve(self):
        """Testing if recipe detail retrieval is successful."""

        tag = sample_tag(user=self.user, name='Dessert')

        ingredient = sample_ingredient(user=self.user, name='Onion')

        recipe = sample_recipe(user=self.user)
        recipe.tags.add(tag)
        recipe.ingredients.add(ingredient)

        url = detail_url(recipe.id)

        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_recipe(self):
        """Testing if a basic recipe can be created."""

        payload = {
            'title': 'Boiled Rice',
            'time_in_minutes': 10,
            'price': 2.00,
        }

        res = self.client.post(RECIPES_URL, payload)

        recipe = Recipe.objects.get(id=res.data['id'])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """Testing if a recipe can be created with tags."""

        tag1 = sample_tag(user=self.user, name='Vegan')
        tag2 = sample_tag(user=self.user, name='Dessert')

        payload = {
            'title': 'Avocado Lime Cheesecake',
            'tags': [tag1.id, tag2.id],
            'time_in_minutes': 45,
            'price': 18.00,
        }

        res = self.client.post(RECIPES_URL, payload)

        recipe = Recipe.objects.get(id=res.data['id'])

        tags = recipe.tags.all()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """Testing if a recipe can be created with ingredients."""

        ingredient1 = sample_ingredient(user=self.user, name='Prawn')
        ingredient2 = sample_ingredient(user=self.user, name='Ginger')

        payload = {
            'title': 'Thai Praw Red Curry',
            'ingredients': [ingredient1.id, ingredient2.id],
            'time_in_minutes': 45,
            'price': 18.00,
        }

        res = self.client.post(RECIPES_URL, payload)

        recipe = Recipe.objects.get(id=res.data['id'])

        ingredients = recipe.ingredients.all()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_partial_update_recipe(self):
        """Testing if a recipe can be updated partially:PATCH."""

        recipe = sample_recipe(user=self.user)

        tag = sample_tag(user=self.user)
        recipe.tags.add(tag)

        ingredient = sample_ingredient(user=self.user)
        recipe.ingredients.add(ingredient)

        new_tag = sample_tag(user=self.user, name='Dessert')

        payload = {
            "title": 'Coconut Salad',
            "tags": [new_tag.id]
        }

        url = detail_url(recipe.id)

        res = self.client.patch(url, payload)

        recipe.refresh_from_db()

        new_tags = recipe.tags.all()

        ingredients = recipe.ingredients.all()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.title, payload['title'])
        self.assertIn(ingredient, ingredients)
        self.assertIn(new_tag, new_tags)
        self.assertNotIn(tag, new_tags)

    def test_fully_update_recipe(self):
        """Testing if a recipe can be updated fully:PUT."""

        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        payload = {
            "title": 'Coconut Salad',
            "time_in_minutes": 15,
            "price": 23.00,
        }

        url = detail_url(recipe.id)

        res = self.client.put(url, payload)

        recipe.refresh_from_db()

        tags = recipe.tags.all()

        ingredients = recipe.ingredients.all()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_in_minutes, payload['time_in_minutes'])
        self.assertEqual(recipe.price, payload['price'])
        self.assertEqual(tags.count(), 0)
        self.assertEqual(ingredients.count(), 0)
