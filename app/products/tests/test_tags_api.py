"""Test for Tag API."""

from decimal import Decimal
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Product, Tag

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

    def test_create_tag_successful(self):
        """Test creating a tag is successful"""
        payload = {'name': 'sample tag'}

        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Tag.objects.count(), 1)
        tag = Tag.objects.get()
        self.assertEqual(tag.name, payload['name'])
        self.assertEqual(tag.user, self.user)

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

    def test_update_tag(self):
        """Test update tag."""
        tag = Tag.objects.create(user=self.user, name='kichen')

        payload = {'name': 'New kichen products'}
        url = detail_url(tag.id)

        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        """Test deleting a tag."""
        tag = Tag.objects.create(user=self.user, name='sample tag')

        url = detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())

    def test_filter_tag_assigned_to_product(self):
        """Test listing tags to those assigned to product."""
        tag1 = Tag.objects.create(user=self.user, name='Meal')
        tag2 = Tag.objects.create(user=self.user, name='Shoes')
        product = Product.objects.create(
            user=self.user,
            name="Sample Product",
            description="This is a test product.",
            price=Decimal('99.99'),
            stock=10,
            image=None,
        )
        product.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)

        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)
        self.assertEqual(len(res.data), 1)
