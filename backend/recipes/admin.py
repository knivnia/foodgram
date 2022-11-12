from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Cart,
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredients,
    Subscription,
    Tag)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    list_filter = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'name',
        'image',
        'text',
        'cooking_time',
        'get_favorites'
    )
    list_filter = (
        'name',
        'author',
        'tags',
    )

    def get_favorites(self, obj):
        return obj.favorites.count()
    get_favorites.short_description = 'favorites'


@admin.register(RecipeIngredients)
class RecipeIngredientsAdmin(admin.ModelAdmin):
    list_display = (
        'recipe',
        'ingredients',
        'amount',
    )
    list_filter = ('recipe', 'ingredients')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'color_display',
        'slug',
    )

    def color_display(self, obj):
        return format_html(
            f'<span style="background: {obj.color};'
            f'color: {obj.color}";>____</span>'
        )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe'
    )


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe'
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author'
    )
