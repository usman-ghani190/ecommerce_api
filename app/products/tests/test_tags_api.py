"""Test for Tag API."""

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from products.serializers import TagSerializer


TAGS_URL = reverse('products:tag-list')


def detail_url(tag_id):
    """Create and return a tag detail url"""
    return reverse('products:tag-detail', args=[tag_id])


def create_user(email='user@example.com', password='user123'):
    """Test for creating and return a new user."""
    return get_user_model().objects.create_user(email, password)


class PublicTagAPITest(TestCase):
    """Test unauthorized API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_reqiured(self):
        """Test authentication is required"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagAPITest(TestCase):
    """Test authorized API requests."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test for retreiving list of Tags API"""
        Tag.objects.create(user=self.user, name='Weekly best products')
        Tag.objects.create(user=self.user, name='Monthly best products')

        res = self.client.get(TAGS_URL)

        tag = Tag.objects.filter(user=self.user).order_by('-name')
        serializer = TagSerializer(tag, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test list of tags limited to authenticated users."""
        user2 = create_user(email='user2@example.com')
        Tag.objects.create(user=user2, name='Best Shoes')
        tag = Tag.objects.create(user=self.user, name='Best Bags')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.filter(user=self.user)
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)
