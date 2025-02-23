from decimal import Decimal
from django.test import TestCase
from core.models import Product


class ProductModelTest(TestCase):
    def setUp(self):
        """Create a sample product for testing."""
        self.product = Product.objects.create(
            name="Test Product",
            description="This is a test product.",
            price=Decimal('99.99'),
            stock=10,
            category="Electronics",
            image=None,  # No image for this test
        )

    def test_product_creation(self):
        """Test that a Product instance is created successfully."""
        self.assertEqual(self.product.name, "Test Product")
        self.assertEqual(self.product.description, "This is a test product.")
        self.assertEqual(self.product.price, Decimal('99.99'))
        self.assertEqual(self.product.stock, 10)
        self.assertEqual(self.product.category, "Electronics")

    def test_product_str(self):
        """Test the string representation of the Product model."""
        self.assertEqual(str(self.product), "Test Product")
