from django.test import TestCase
from django.contrib.auth import get_user_model


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
