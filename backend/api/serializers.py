from django.shortcuts import get_object_or_404

from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from recipes.models import (Cart, Favorite, Ingredient, Recipe,
                            RecipeIngredients, Subscription, Tag)
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous or (user == obj):
            return False
        return Subscription.objects.filter(
            user=user,
            author=obj
        ).exists()

    class Meta:
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )
        model = User


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class AddIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredients')

    def create(self, validated_data):
        return RecipeIngredients.objects.create(
            ingredients=validated_data.get('id'),
            amount=validated_data.get('amount')
        )

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'amount')


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredients.id')
    name = serializers.ReadOnlyField(source='ingredients.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit'
    )

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    image = Base64ImageField(
        required=True,
        allow_null=False,
        max_length=None,
        use_url=True
    )
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(read_only=True, many=True)

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Cart.objects.filter(user=user, recipe_id=obj.id).exists()

    def get_ingredients(self, obj):
        ingredients = RecipeIngredients.objects.filter(recipe=obj)
        return RecipeIngredientsSerializer(ingredients, many=True).data

    def add_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            RecipeIngredients.objects.create(
                recipe=recipe,
                ingredients_id=ingredient.get('id'),
                amount=ingredient.get('amount'),
            )

    def create(self, validated_data):
        tags_data = self.initial_data.get('tags')
        ingredients_data = self.initial_data.get('ingredients')
        ingredients_list = []
        for ingredient in ingredients_data:
            if ingredient.get('id') in ingredients_list:
                ingredient_name = get_object_or_404(
                    Ingredient,
                    id=ingredient.get('id')
                )
                raise serializers.ValidationError(
                    f'Ingredient {ingredient_name} is duplicated!'
                )
            ingredients_list.append(ingredient.get('id'))
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        self.add_ingredients(ingredients_data, recipe)
        return recipe

    def update(self, instance, validated_data):
        recipe = Recipe.objects.get(id=instance.id)
        if 'tags' in self.initial_data:
            recipe.tags.clear()
            tags_data = self.initial_data.get('tags')
            recipe.tags.set(tags_data)
        if 'ingredients' in self.initial_data:
            RecipeIngredients.objects.filter(recipe=recipe).all().delete()
            recipe.ingredients.clear()
            ingredients_data = self.initial_data.get('ingredients')
            self.add_ingredients(ingredients_data, recipe)
        recipe.image = validated_data.get('image')
        recipe.cooking_time = validated_data.get('cooking_time')
        recipe.save()
        return recipe

    class Meta:
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )
        model = Recipe


class ShortRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'


class SubscriptionSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        return Subscription.objects.filter(
            user=obj.user,
            author=obj.author
        ).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj.author)
        if recipes_limit:
            queryset = queryset[:int(recipes_limit)]
        return ShortRecipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()

    def validate(self, data, pk):
        if self.request.user.id == pk:
            raise serializers.ValidationError("Selfsubscription!")
        if Subscription.objects.filter(
                user_id=self.request.user.id,
                author_id=pk).exists():
            raise serializers.ValidationError(
                'Already subscribed!')
        return data

    class Meta:
        model = Subscription
        fields = ('id',
                  'email',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed',
                  'recipes',
                  'recipes_count')
