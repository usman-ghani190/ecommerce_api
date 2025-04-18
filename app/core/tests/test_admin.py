"""Tests for Django admin modifications."""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client


LISTED_USERS_URL = reverse('admin:core_user_changelist')
CREATE_USER_URL = reverse('admin:core_user_add')


class AdminSiteTests(TestCase):
    """Test for Django admin site."""
    def setUp(self):
        """Setup for tests."""
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@example.com',
            password='test123',
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='test123',
            name='Test User',
        )

    def test_users_listed(self):
        """Test that users are listed on user page."""
        res = self.client.get(LISTED_USERS_URL)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_edit_user_page(self):
        """Test that the edit user page works."""
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """Test that the create user page works."""
        res = self.client.get(CREATE_USER_URL)

        self.assertEqual(res.status_code, 200)
