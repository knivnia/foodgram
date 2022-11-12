from django.db import models

from api.validators import hex_code_validator
from users.models import User


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Tag',
        help_text='Choose tag for your recipe',
        unique=True,
        max_length=50)
    color = models.CharField(
        default='#0000ff',
        verbose_name='Color code',
        help_text='Choose color HEX-code ',
        unique=True,
        max_length=7,
        validators=[hex_code_validator, ])
    slug = models.SlugField(
        verbose_name='Tag slug',
        help_text='Type unique tag slug',
        unique=True,
        max_length=20)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Ingredient',
        help_text='Add ingredient to your recipe',
        max_length=250
    )
    measurement_unit = models.CharField(
        verbose_name='Units',
        help_text='Add units for this ingredient',
        max_length=50
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Recipe'
    )
    name = models.CharField(
        unique=True,
        verbose_name='Recipe name',
        help_text='Recipe name',
        max_length=50)
    image = models.ImageField(
        verbose_name='Image',
        upload_to='recipes/',
        blank=True,
        help_text='Upload your image'
    )
    text = models.TextField(
        verbose_name='Text',
        help_text='Type your recipe'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredients',
        verbose_name='Ingredients',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Tags',
        related_name='+',
    )
    cooking_time = models.IntegerField(
        verbose_name='Cooking time',
        help_text='Enter cooking time for your recipe'
    )
    pub_date = models.DateTimeField(
        verbose_name='Publication date',
        auto_now_add=True,
    )

    def __str__(self):
        return self.name


class RecipeIngredients(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Recipe',
        related_name='recipeingredients',
        on_delete=models.CASCADE
    )
    ingredients = models.ForeignKey(
        Ingredient,
        verbose_name='Ingredient',
        related_name='+',
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Ingredient amount',
        help_text='Add how much of ingredient you need for your recipe',
        default=0
    )


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscription',
        verbose_name='Author'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique subscription'
            ),
            models.CheckConstraint(
                check=~models.Q(author=models.F('user')),
                name='self_subscription'
            )
        ]


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='User',
        related_name='favorites',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Recipe',
        related_name='favorites',
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique favorite recipe'
            ),
        ]


class Cart(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='User',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Recipe',
        related_name='cart',
        on_delete=models.CASCADE
    )
