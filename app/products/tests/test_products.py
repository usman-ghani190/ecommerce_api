"""Tests for Product API."""

from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Product

from products.serializers import ProductSerializer

PRODUCT_URL = reverse('products:product-list')


def detail_url(product_id):
    """Create and return a Product detail url."""
    return (reverse('products:product-detail', args=[product_id]))


def create_product(user, **params):
    """Create and return sample product"""
    defaults = {
        'name': 'Sample Product',
        'description': 'Sample description',
        'price': Decimal('99.99'),
        'stock': 5,
        'category': 'Sample Category',
    }
    defaults.update(params)

    product = Product.objects.create(user=user, **defaults)
    return product


def create_user(**params):
    """Create and return a user."""
    return get_user_model().objects.create_user(**params)


class PublicProductAPITest(TestCase):
    """Test unauthenticated API tests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test authentication require to call API."""

        res = self.client.get(PRODUCT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateProductAPITests(TestCase):
    """Test for authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='test@example.com',
            password='testpassword',
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_products(self):
        """Test retriving  list of products"""
        create_product(user=self.user)
        create_product(user=self.user)

        res = self.client.get(PRODUCT_URL)

        product = Product.objects.all().order_by('id')
        serializer = ProductSerializer(product, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_product_list_limited_to_user(self):
        """Test list of products is limited to authentiated users."""
        other_user = create_user(email='other@example.com', password='123')
        create_product(user=other_user)
        create_product(user=self.user)

        res = self.client.get(PRODUCT_URL)

        product = Product.objects.filter(user=self.user)

        serializer = ProductSerializer(product, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_product_detail(self):
        """Test to get product details"""
        product = create_product(user=self.user)

        url = detail_url(product.id)
        res = self.client.get(url)

        serializer = ProductSerializer(product)
        self.assertEqual(res.data, serializer.data)

    def test_create_product(self):
        """Test creatin g a product"""
        payload = {
            'name': 'bag',
            'description': 'Sample description',
            'price': 30.00,
            'stock': 4,
            'category': 'Bags',
        }
        res = self.client.post(PRODUCT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        product = Product.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(product, k), v)
        self.assertEqual(product.user, self.user)

    def test_partial_update(self):
        """Test partial update of product"""
        product = create_product(
            user=self.user,
            name='sample name',
        )
        payload = {'name': 'New sample name'}
        url = detail_url(product.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        product.refresh_from_db()
        self.assertEqual(product.name, payload['name'])
        self.assertEqual(product.user, self.user)

    def test_full_update(self):
        """Test full update of product"""
        product = create_product(
            user=self.user,
            name='sample name',
        )
        payload = {
            'name': 'new product',
            'description': 'new description',
            'price': 30,
            'stock': 5,
            'category': 'new category',
        }
        url = detail_url(product.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        product.refresh_from_db()

        for k, v in payload.items():
            self.assertEqual(getattr(product, k), v)
        self.assertEqual(product.user, self.user)
