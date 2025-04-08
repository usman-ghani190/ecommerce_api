"""Views for Product API."""

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Cart, CartItem, Category, Product, Tag, Wishlist
from products import serializers


class ProductViewSet(viewsets.ModelViewSet):
    """View for for manage Product API."""
    serializer_class = serializers.ProductSerializer
    queryset = Product.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def _params_to_ints(self, qs):
        """Convert a list of strings into integers."""
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """Retrieve recipes for authenticated user."""
        tags = self.request.query_params.get('tags')
        categories = self.request.query_params.get('categories')
        queryset = self.queryset
        if tags:
            tags_id = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tags_id)
        if categories:
            category_ids = self._params_to_ints(categories)
            queryset = queryset.filter(categories__id__in=category_ids)
        return queryset.filter(
            user=self.request.user
        ).order_by('-id').distinct()


class TagViewSet(viewsets.ModelViewSet):
    """Manage tags in the database."""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset to authenticated user and assigned tags"""
        queryset = self.queryset.filter(user=self.request.user)
        assigned_only = bool(self.request.query_params.get('assigned_only'))
        if assigned_only:
            queryset = queryset.filter(product__isnull=False).distinct()
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CategoryViewSet(viewsets.ModelViewSet):
    """Manage categories in database."""
    serializer_class = serializers.CategorySerializer
    queryset = Category.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset to authenticated user and assigned categories"""
        queryset = self.queryset.filter(user=self.request.user)
        assigned_only = bool(self.request.query_params.get('assigned_only'))
        if assigned_only:
            queryset = queryset.filter(products__isnull=False).distinct()
        return queryset

    def perform_create(self, serializer):
        """Create a new category"""
        serializer.save(user=self.request.user)


class CartViewSet(viewsets.ModelViewSet):
    """Manage carts in the database."""
    serializer_class = serializers.CartSerializer
    queryset = Cart.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return carts for the authenticated user only."""
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Create a new cart for the authenticated user."""
        serializer.save(user=self.request.user)


class CartItemViewSet(viewsets.ModelViewSet):
    """Manage items in a user's cart."""
    serializer_class = serializers.CartItemSerializer
    queryset = CartItem.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return cart items for the authenticated user's carts."""
        return self.queryset.filter(cart__user=self.request.user)


class WishlistViewSet(viewsets.ModelViewSet):
    """Manage wishlists for users."""
    serializer_class = serializers.WishlistSerializer
    queryset = Wishlist.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return wishlist for the authenticated user."""
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Create a wishlist for the authenticated user."""
        serializer.save(user=self.request.user)
