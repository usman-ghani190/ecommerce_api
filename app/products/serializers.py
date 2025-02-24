"""Serializer for product API."""

from rest_framework import serializers

from core.models import Product


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product."""
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'description',
            'price',
            'stock',
            'category',
            'image'
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
