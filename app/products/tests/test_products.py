"""Tests for Product API."""

from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Category, Product, Tag

from products.serializers import ProductSerializer

PRODUCT_URL = reverse('products:product-list')


def detail_url(product_id):
    """Create and return a Product detail url."""
    return reverse('products:product-detail', args=[product_id])


def create_product(user, **params):
    """Create and return a sample product."""
    defaults = {
        'name': 'Sample Product',
        'description': 'Sample description',
        'price': Decimal('99.99'),
        'stock': 5,
    }
    defaults.update(params)

    product = Product.objects.create(user=user, **defaults)

    if 'category' in params:
        category, created = Category.objects.get_or_create(
            name=params['category'],
            defaults={"user": user}
        )
        product.categories.add(category)

    if 'tags' in params:
        tags = [Tag.objects.get_or_create(
            name=tag['name'], defaults={"user": user}
        )[0] for tag in params['tags']]
        product.tags.set(tags)

    return product


def create_user(**params):
    """Create and return a user."""
    return get_user_model().objects.create_user(**params)


class PublicProductAPITest(TestCase):
    """Test unauthenticated API tests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test authentication is required to call API."""

        res = self.client.get(PRODUCT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateProductAPITests(TestCase):
    """Test for authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@example.com",
            password="testpass123"
        )
        self.client.force_authenticate(user=self.user)

        self.category, _ = Category.objects.get_or_create(
            name="Test Category",
            user=self.user,
        )
        self.tags, created = Tag.objects.get_or_create(
            name="Sample Tag",
            user=self.user,
        )

    def test_retrieve_products(self):
        """Test retrieving a list of products"""
        create_product(user=self.user)
        create_product(user=self.user)

        res = self.client.get(PRODUCT_URL)

        products = Product.objects.all().order_by('-id')
        serializer = ProductSerializer(products, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_product_list_limited_to_user(self):
        """Test that product list is limited to authenticated user."""
        other_user = create_user(email='other@example.com', password='123')
        create_product(user=other_user)
        create_product(user=self.user)

        res = self.client.get(PRODUCT_URL)

        products = Product.objects.filter(user=self.user)
        serializer = ProductSerializer(products, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_product_detail(self):
        """Test retrieving product details"""
        product = create_product(user=self.user)

        url = detail_url(product.id)
        res = self.client.get(url)

        serializer = ProductSerializer(product)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_product(self):
        """Test creating a product"""
        self.client.force_authenticate(user=self.user)  # Authenticate user

        unique_category_name = "Unique Category"
        unique_tag_name = "Unique Tag"

        payload = {
            'name': 'bag',
            'description': 'Sample description',
            'price': Decimal('30.00'),
            'stock': 4,
            'category': unique_category_name,  # Pass category name directly
            'tags': [{'name': unique_tag_name}],  # Use dictionary for tags
        }

        res = self.client.post(PRODUCT_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        product = Product.objects.get(id=res.data['id'])
        self.assertEqual(product.name, payload['name'])
        self.assertEqual(product.user, self.user)
        self.assertTrue(
            set([tag.name for tag in product.tags.all()]).issubset(
                set([tag['name'] for tag in payload['tags']])),
        )
        self.assertTrue(
            set(
                [category.name for category in product.categories.all()]
            ).issubset(
                set([payload['category']])),
        )

    def test_partial_update(self):
        """Test partial update of a product"""
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
        """Test full update of a product"""
        product = create_product(
            user=self.user,
            name='sample name',
        )
        payload = {
            'name': 'new product',
            'description': 'new description',
            'price': Decimal('30.00'),
            'stock': 5,
            'category': 'Updated Category',
            'tags': [{'name': 'Updated Tag'}],
        }
        url = detail_url(product.id)
        res = self.client.put(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        product.refresh_from_db()

        for k, v in payload.items():
            if k in ['category', 'tags']:
                continue
            self.assertEqual(getattr(product, k), v)
        self.assertTrue(
            set(
                [category.name for category in product.categories.all()]
            ).issubset(
                set([payload['category']])),
        )
        self.assertTrue(
            set([tag.name for tag in product.tags.all()]).issubset(
                set([tag['name'] for tag in payload['tags']])),
        )
        self.assertEqual(product.user, self.user)

    def test_delete_product(self):
        """Test deleting a product."""
        product = create_product(user=self.user)

        url = detail_url(product.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(id=product.id).exists())

    def test_user_cannot_access_other_users_products(self):
        """Ensure a user cannot retrieve another user's product details."""
        other_user = create_user(
            email="other@example.com",
            password="testpass123"
        )
        product = create_product(user=other_user)

        url = detail_url(product.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_update_other_users_product(self):
        """Ensure a user cannot update another user's product."""
        other_user = create_user(
            email="other@example.com",
            password="testpass123"
        )
        product = create_product(user=other_user)

        payload = {'name': 'Hacked Product'}
        url = detail_url(product.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_delete_other_users_product(self):
        """Ensure a user cannot delete another user's product."""
        other_user = create_user(
            email="other@example.com",
            password="testpass123"
        )
        product = create_product(user=other_user)

        url = detail_url(product.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
