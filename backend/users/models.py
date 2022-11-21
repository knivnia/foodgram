from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from .validators import UsernameValidator


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name'
    ]

    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[
            UnicodeUsernameValidator(),
            UsernameValidator('me')
        ]
    )
    email = models.EmailField(
        max_length=254,
        unique=True
    )
    first_name = models.CharField(
        max_length=150,
        blank=False,
        null=False
    )
    last_name = models.CharField(
        max_length=150,
        blank=False,
        null=False
    )

    def __str__(self):
        return self.username

    class Meta:
        ordering = ('id', )
