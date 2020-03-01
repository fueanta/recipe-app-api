from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test cases for unauthenticated User API operations."""

    def setUp(self):
        self.client = APIClient()

    def test_successful_creation_of_valid_user(self):
        """Testing if creation of user with valid payload is successful."""

        payload = {
            "email": 'test@fueanta.com',
            "password": '123456',
            "name": 'Test User',
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        created_user = get_user_model().objects.get(**res.data)
        self.assertTrue(created_user.check_password(payload['password']))

        self.assertNotIn('password', res.data)

    def test_detection_of_user_already_exists(self):
        """Testing if the creation of existed user fails."""

        payload = {
            "email": 'test@fueanta.com',
            "password": 'anypass312',
            "name": 'Test User',
        }

        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Testing if user creation fails with password less than 6 chars."""

        payload = {
            "email": 'test@fueanta.com',
            "password": 'passu',
            "name": 'Test User',
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_for_user(self):
        """Testing if token is created for user."""

        payload = {
            "email": 'test@fueanta.com',
            "password": 'pass123',
        }

        create_user(**payload)

        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_token_not_created_for_invalid_credentials(self):
        """Testing if token is missing for invalid credentials."""

        payload = {
            "email": 'test@fueanta.com',
            "password": 'pass123',
        }

        create_user(**payload)

        payload["password"] = 'WrongPass'

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_token_not_created_for_not_found_user(self):
        """Testing if token is missing when user not found."""

        payload = {
            "email": 'test@fueanta.com',
            "password": 'pass123',
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_token_not_created_for_missing_fields(self):
        """Testing if token is missing for missing fields."""

        payload = {
            "email": '',
            "password": '',
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthorized_user_data_retrieval(self):
        """Testing if authentication is required for managing user data."""

        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test cases for authenticated User API operations."""

    def setUp(self):
        self.user = create_user(
            email='test@fueanta.com',
            password='123456',
            name='Test User',
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_successful_fetch_self_user_data(self):
        """Testing if authenticated user can retrieve self-data."""

        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            "email": self.user.email,
            "name": self.user.name,
        })

    def test_successful_update_self_user_data(self):
        """Testing if authenticated user can update self-data."""

        payload = {
            "name": 'New Name',
            "password": 'newpass123',
        }

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))

    def test_post_not_allowed_on_ME_url(self):
        """Testing if POST request is forbidden on ME url."""

        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
