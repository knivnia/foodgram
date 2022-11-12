from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import UsernameValidator


class User(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[UsernameValidator('me'), ]
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        null=False,
        blank=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name'
    ]

    class Meta:
        ordering = ('id', )
