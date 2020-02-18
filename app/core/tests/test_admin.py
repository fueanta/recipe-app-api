from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model


class AdminSiteTests(TestCase):

    def setUp(self):
        """
        Creates users and forces admin login.
        """
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
        """
        Test: Users are listed on admin site.
        """
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_user_change_page(self):
        """
        Test: User edit page works.
        """
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """
        Test: Create user page works.
        """
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
