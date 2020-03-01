from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from core import models


def sample_user(email='test@fueanta.com', password='test3214'):
    """Creates and returns a sample user for test purposes."""

    return get_user_model().objects.create_user(email, password)


class TestUserModel(TestCase):
    """Test cases for custom User model."""

    def test_create_user(self):
        """Testing if the user is created successfully."""

        email = 'test@test.com'
        password = 'TestPass123'

        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Testing if the email of the new user has been normalized."""

        email = "test@FUEANTA.COM"
        user = get_user_model().objects.create_user(email=email)
        self.assertEqual(user.email, email.lower())

    def test_raise_value_error_for_new_user_empty_email(self):
        """Testing if a ValueError is raised if user provided no email."""

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(email=None)

    def test_create_superuser(self):
        """Testing if a superuser is created successfully."""

        user = get_user_model().objects.create_superuser(
            email='test@fueanta.com',
            password='test123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_object_representation(self):
        """Testing if a tag object is represented by its name."""

        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan'
        )

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_object_representation(self):
        """Testing if an ingredient object is represented by its name."""

        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='Cucumber'
        )

        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_object_representation(self):
        """Testing if a recipe object is represented by its title."""

        recipe = models.Recipe.objects.create(
            title='Sreak and mashroom sauce',
            time_in_minutes=5,
            price=2.00,
            user=sample_user(),
        )

        self.assertEqual(str(recipe), recipe.title)

    @patch('uuid.uuid4')
    def test_image_filename_uuid(self, mock_uuid):
        """Testing if image is saved correctly."""

        uuid = 'mock-uuid'

        mock_uuid.return_value = uuid

        file_path = models.image_file_path(None, 'myimage.jpg')

        exp_path = f'uploads/images/{uuid}.jpg'

        self.assertEqual(file_path, exp_path)
