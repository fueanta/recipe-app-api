from django.test import TestCase
from django.contrib.auth import get_user_model


class TestModels(TestCase):
    def test_create_user(self):
        """
        Testing if the user is created successfully
        """
        email = 'test@test.com'
        password = 'TestPass123'

        user = get_user_model().objects.create_user(
            username=email,
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
