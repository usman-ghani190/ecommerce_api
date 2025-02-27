"""Urls for managing product API views."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from products import views

router = DefaultRouter()
router.register('products', views.ProductViewSet)
router.register('tags', views.TagViewSet)
router.register('categories', views.CategoryViewSet)

app_name = 'products'

urlpatterns = [
    path('', include(router.urls)),
]
