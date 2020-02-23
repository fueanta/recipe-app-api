from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


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
