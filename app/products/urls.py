"""Urls for managing product API views."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from products import views

router = DefaultRouter()
router.register('products', views.ProductViewSet)
router.register('tags', views.TagViewSet)
router.register('categories', views.CategoryViewSet)
router.register('cart', views.CartViewSet)
router.register('cartitem', views.CartItemViewSet)
router.register('wishlist', views.WishlistViewSet)

app_name = 'products'

urlpatterns = [
    path('', include(router.urls)),
    path('create-payment-intent/',
         views.CreateStripePaymentIntent.as_view(),
         name='create-payment-intent'),
]
