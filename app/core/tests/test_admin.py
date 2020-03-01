from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse


class AdminSiteTests(TestCase):
    """Test cases for admin site functionality."""

    def setUp(self):
        """Creates users and forces admin to login."""
        self.client = Client()

        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@fueanta.com',
            password='admin1234',
            name='Admin User'
        )
        self.client.force_login(self.admin_user)

        self.user = get_user_model().objects.create_user(
            email='test@fueanta.com',
            password='test1234',
            name='Test User'
        )

    def test_users_listed(self):
        """Testing if the users are listed on admin site."""

        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_user_change_page(self):
        """Testing if the User model edit page works on admin site."""

        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """Testing if the User model create page works on admin site."""

        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
