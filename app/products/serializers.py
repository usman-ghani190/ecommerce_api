"""Serializer for product API."""

from rest_framework import serializers

from core.models import Category, Product, Tag


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag"""
    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category"""
    class Meta:
        model = Category
        fields = ['id', 'name']
        read_only_fields = ['id']


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product."""

    category = serializers.CharField()
    tags = TagSerializer(many=True)  # Use TagSerializer for tags

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'description',
            'price',
            'stock',
            'category',
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
        category_name = validated_data.pop('category')
        tags = validated_data.pop('tags')
        validated_data.pop('user', None)

        category, created = self._get_or_create_category(category_name, user)
        tag_objs = self._get_or_create_tags(tags, user)

        product = Product.objects.create(
            category=category,
            user=user,
            **validated_data
        )
        product.tags.set(tag_objs)
        return product

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        category_name = validated_data.pop('category', None)
        if tags is not None:
            instance.tags.clear()
            tag_objs = self._get_or_create_tags(tags, instance.user)
            instance.tags.set(tag_objs)
        if category_name is not None:
            category, created = self._get_or_create_category(
                category_name,
                instance.user
            )
            instance.category = category

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
