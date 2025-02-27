"""Test for Category API."""

from decimal import Decimal
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Category, Product

from products.serializers import CategorySerializer


CATEGORY_URL = reverse('products:category-list')


def detail_url(category_id):
    """Create and return a detail url."""
    return reverse('products:category-detail', args=[category_id])


def create_user(email='abs@example.com', password='123456'):
    """Create and return user"""
    return get_user_model().objects.create_user(email, password)


class PublicCategoryAPITest(TestCase):
    """Test unauthrized API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_is_required(self):
        """Test authentication is required"""
        res = self.client.get(CATEGORY_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateCategoryAPITest(TestCase):
    """Test for authenticated API requests."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_create_category_successful(self):
        """Test creating a category is successful"""
        payload = {'name': 'Electronics'}

        res = self.client.post(CATEGORY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 1)
        self.assertEqual(Category.objects.get().name, payload['name'])

    def test_retrieve_categories(self):
        """Test for retrieving list of cetegories"""
        Category.objects.create(user=self.user, name='Best shoes')
        Category.objects.create(user=self.user, name='kichen')

        res = self.client.get(CATEGORY_URL)

        category = Category.objects.all().order_by('name')
        serializer = CategorySerializer(category, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_categories_limited_to_user(self):
        """Test categories are limited to authenticated user"""
        other_user = create_user(email='other@example.com')

        Category.objects.create(user=other_user, name='sample category')
        category = Category.objects.create(
            user=self.user,
            name='new sample category'
        )

        res = self.client.get(CATEGORY_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], category.name)

    def test_updating_category(self):
        """Test updating a category."""
        category = Category.objects.create(user=self.user, name='category')
        payload = {'name': 'new category'}

        url = detail_url(category.id)
        res = self.client.patch(url, payload)

        category.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(category.name, payload['name'])

    def test_deleting_category(self):
        """Test deleting a category"""
        category = Category.objects.create(user=self.user, name='shoes')

        url = detail_url(category.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        categories = Category.objects.filter(id=category.id)
        self.assertFalse(categories.exists())

    def test_filter_category_assigned_to_product(self):
        """Test filtering categories that are assigned to products"""
        category1 = Category.objects.create(user=self.user, name='Cycles')
        category2 = Category.objects.create(user=self.user, name='Motors')

        product = Product.objects.create(
            user=self.user,
            name='Gear Cycle',
            description="This is a test product.",
            price=Decimal('40.5'),
            stock=10,
            image=None,
        )
        product.categories.add(category1)

        res = self.client.get(CATEGORY_URL, {'assigned_only': 1})

        s1 = CategorySerializer(category1)
        s2 = CategorySerializer(category2)

        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)
