"""Django models"""

from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,)


class UserManager(BaseUserManager):
    """Manager for user profiles"""
    def create_user(self, email, password=None, **extra_fields):
        """Create a new user profile"""
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """Create and save a new superuser with given details"""
        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that supports using email instead of username"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Tag(models.Model):
    """Tag object"""
    name = models.CharField(max_length=255, unique=True)
    user = models.ForeignKey(
     settings.AUTH_USER_MODEL,
     on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name


class Category(models.Model):
    """Category object"""
    name = models.CharField(max_length=255, unique=True)
    user = models.ForeignKey(
     settings.AUTH_USER_MODEL,
     on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name


class Product(models.Model):
    """Product object"""
    user = models.ForeignKey(
     settings.AUTH_USER_MODEL,
     on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True
    )
    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return self.name
