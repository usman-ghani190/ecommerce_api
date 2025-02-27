"""Serializer for product API."""

from rest_framework import serializers

from core.models import Category, Product, Tag


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag"""
    class Meta:
        model = Tag
        fields = ['id', 'name', 'user']
        read_only_fields = ['id', 'user']


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category"""
    class Meta:
        model = Category
        fields = ['id', 'name']
        read_only_fields = ['id']


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product."""

    categories = CategorySerializer(many=True, required=False)
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'description',
            'price',
            'stock',
            'categories',
            'tags',
            'user'
        ]
        read_only_fields = ['id', 'user']

    def _get_or_create_category(self, category_name, user):
        """Get or create category."""
        return Category.objects.get_or_create(
            name=category_name,
            defaults={'user': user}
        )

    def _get_or_create_tags(self, tags, user):
        """Get or create tags."""
        tag_objs = []
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                name=tag['name'],
                defaults={'user': user}
            )
            tag_objs.append(tag_obj)
        return tag_objs

    def create(self, validated_data):
        """Create a product."""
        user = self.context['request'].user
        categories_data = validated_data.pop('categories', [])
        tags_data = validated_data.pop('tags', [])
        validated_data.pop('user', None)

        product = Product.objects.create(
            user=user,
            **validated_data
        )
        self._create_or_update_categories(product, categories_data)
        self._create_or_update_tags(product, tags_data)
        return product

    def update(self, instance, validated_data):
        categories_data = validated_data.pop('categories', None)
        tags_data = validated_data.pop('tags', None)
        if categories_data is not None:
            instance.categories.clear()
            self._create_or_update_categories(instance, categories_data)
        if tags_data is not None:
            instance.tags.clear()
            self._create_or_update_tags(instance, tags_data)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    def _create_or_update_categories(self, product, categories_data):
        """Handle creating or updating categories"""
        for category_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=category_data['name'],
                defaults={'user': self.context['request'].user}
            )
            product.categories.add(category)

    def _create_or_update_tags(self, product, tags_data):
        """Handle creating or updating tags"""
        for tag_data in tags_data:
            tag, created = Tag.objects.get_or_create(
                name=tag_data['name'],
                defaults={'user': self.context['request'].user}
            )
            product.tags.add(tag)
