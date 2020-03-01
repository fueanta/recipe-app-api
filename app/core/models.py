import os
import uuid

from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.db import models


def image_file_path(instance, filename):
    """Generate image file path for newly uploaded image."""

    ext = filename.split('.')[-1]

    new_filename = f'{uuid.uuid4()}.{ext}'

    return os.path.join('uploads/images/', new_filename)


class UserManager(BaseUserManager):
    """Manager class for custom User model."""

    def create_user(self, email, password=None, **extra_fields):
        """Creates and saves a new user."""
        if not email:
            raise ValueError('User must provide an email address.')

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password, **extra_fields):
        """Creates and saves a new admin level user."""

        user = self.create_user(email, password, **extra_fields)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that supports the use of email instead of username."""

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Tag(models.Model):
    """Tag model, to be used for a recipe."""

    name = models.CharField(max_length=255)
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)

    def __str__(self):
        """Defines the string representation of an object."""

        return self.name


class Ingredient(models.Model):
    """Ingredient model, to be used in a recipe."""

    name = models.CharField(max_length=255)
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)

    def __str__(self):
        """Defines the string representation of an object."""

        return self.name


class Recipe(models.Model):
    """Blueprint for recipe objects."""

    title = models.CharField(max_length=255)
    time_in_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)
    image = models.ImageField(null=True, upload_to=image_file_path)

    ingredients = models.ManyToManyField(Ingredient)
    tags = models.ManyToManyField(Tag)

    user = models.ForeignKey(to=settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)

    def __str__(self):
        """Defines the string representation of an object."""

        return self.title
