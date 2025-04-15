"""Views for Product API."""

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework import viewsets
from drf_spectacular.utils import extend_schema
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
import stripe

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


stripe.api_key = settings.STRIPE_SECRET_KEY


@extend_schema(
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "amount": {
                    "type": "integer",
                    "example": 5000
                }
            },
            "required": ["amount"]
        }
    },
    responses={
        200: {
            "type": "object",
            "properties": {
                "client_secret": {
                    "type": "string",
                    "example": "pi_12345_secret_67890"
                }
            }
        },
        400: {
            "type": "object",
            "properties": {
                "error": {"type": "string"}
            }
        }
    },
    description="Creates a Stripe PaymentIntent and returns a client secret."
)
class CreateStripePaymentIntent(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            amount = int(request.data.get("amount"))
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency='usd',
                metadata={'user_id': request.user.id},
            )
            return Response({
                'client_secret': intent.client_secret
            })
        except Exception as e:
            return Response({"error": str(e)}, status=400)


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = 'your_webhook_secret_from_stripe'

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        print('💰 Payment succeeded:', payment_intent['id'])
        # TODO: mark order as paid in your database
    elif event['type'] == 'payment_intent.payment_failed':
        print('❌ Payment failed')

    return HttpResponse(status=200)
