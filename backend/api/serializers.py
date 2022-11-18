from django.shortcuts import get_object_or_404

from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
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
    id = serializers.ReadOnlyField(source='ingredients.id')

    def create(self, validated_data):
        return RecipeIngredients.objects.create(
            ingredient=validated_data.get('id'),
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
    image = Base64ImageField(required=True, allow_null=False)
    # ingredients = serializers.SerializerMethodField()
    ingredients = AddIngredientsSerializer(read_only=True)
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
        return Cart.objects.filter(recipe_id=obj.id).exists()

    # def get_ingredients(obj):
    #     ingredients = RecipeIngredients.objects.filter(recipe=obj)
    #     return RecipeIngredientsSerializer(ingredients, many=True).data

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
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        self.add_ingredients(ingredients_data, recipe)
        print(f'!!!!INGR    {ingredients_data}')
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


class ShortRecipeSerializer(serializers.HyperlinkedModelSerializer):
    image = Base64ImageField(required=True, allow_null=False)

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


# class IngredientSerializer(serializers.ModelSerializer):
#     """ Сериализатор модели ингредиентов. """
#     class Meta:
#         model = Ingredient
#         fields = (
#             'id',
#             'name',
#             'measurement_unit'
#         )


# class RecipeIngredientsSerializer(serializers.ModelSerializer):
#     """ Сериализатор ингредиентов в рецепте. """
#     id = serializers.PrimaryKeyRelatedField(
#         source='ingredient',
#         read_only=True
#     )
#     measurement_unit = serializers.SlugRelatedField(
#         source='ingredient',
#         slug_field='measurement_unit',
#         read_only=True,
#     )
#     name = serializers.SlugRelatedField(
#         source='ingredient',
#         slug_field='name',
#         read_only=True,
#     )

#     class Meta:
#         model = RecipeIngredients
#         fields = ('id', 'name', 'amount', 'measurement_unit')


# class RecipeSerializer(serializers.ModelSerializer):
#     """ Сериализатор модели рецептов. """
#     tags = TagSerializer(many=True, read_only=True)
#     author = UserSerializer(read_only=True)
#     ingredients = serializers.SerializerMethodField()
#     is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
#     is_favorited = serializers.SerializerMethodField(read_only=True)

#     class Meta:
#         model = Recipe
#         fields = (
#             'id', 'tags', 'author', 'ingredients',
#             'is_favorited', 'is_in_shopping_cart',
#             'name', 'image', 'text', 'cooking_time'
#         )

#     @staticmethod
#     def get_ingredients(obj):
#         ingredients = RecipeIngredients.objects.filter(recipe=obj)
#         return RecipeIngredientsSerializer(ingredients, many=True).data

#     def get_is_favorited(self, obj):
#         request = self.context.get('request')
#         if request.user.is_anonymous:
#             return False
#         return request.user.favorites.filter(recipe=obj).exists()

#     def get_is_in_shopping_cart(self, obj):
#         request = self.context.get('request')
#         if request.user.is_anonymous:
#             return False
#         return request.user.purchases.filter(recipe=obj).exists()


# class AddIngredientSerializer(serializers.ModelSerializer):
#     """ Сериализатор добавления ингредиентов. """
#     id = serializers.PrimaryKeyRelatedField(
#         source='ingredient', queryset=Ingredient.objects.all()
#     )

#     class Meta:
#         model = RecipeIngredients
#         fields = ('id', 'amount')

#     def validate_amount(self, data):
#         if int(data) < 1:
#             raise serializers.ValidationError({
#                 'ingredients': (
#                     'Количество должно быть больше 1'
#                 ),
#                 'msg': data
#             })
#         return data

#     def create(self, validated_data):
#         return RecipeIngredients.objects.create(
#             ingredient=validated_data.get('id'),
#             amount=validated_data.get('amount')
#         )


# class RecipeCreateSerializer(serializers.ModelSerializer):
#     """ Сериализатор создания рецепта. """
#     image = Base64ImageField()
#     author = UserSerializer(read_only=True)
#     ingredients = AddIngredientSerializer(many=True)
#     tags = serializers.PrimaryKeyRelatedField(
#         queryset=Tag.objects.all(), many=True
#     )
#     cooking_time = serializers.IntegerField()

#     class Meta:
#         model = Recipe
#         fields = (
#             'id', 'image', 'tags', 'author', 'ingredients',
#             'name', 'text', 'cooking_time',
#         )

#     def create_ingredients(self, recipe, ingredients):
#         RecipeIngredients.objects.bulk_create([
#             RecipeIngredients(
#                 recipe_parent=recipe,
#                 amount=ingredient['amount'],
#                 ingredient=ingredient['ingredient'],
#             ) for ingredient in ingredients
#         ])

#     def validate(self, data):
#         ingredients = self.initial_data.get('ingredients')
#         ingredients_list = []
#         for ingredient in ingredients:
#             ingredient_id = ingredient['id']
#             if ingredient_id in ingredients_list:
#                 raise serializers.ValidationError(
#                     'Есть повторяющиеся ингредиенты!'
#                 )
#             ingredients_list.append(ingredient_id)
#         if data['cooking_time'] <= 0:
#             raise serializers.ValidationError(
#                 'Время приготовления должно быть больше 0!'
#             )
#         return data

#     def create(self, validated_data):
#         request = self.context.get('request')
#         ingredients = validated_data.pop('ingredients')
#         tags = validated_data.pop('tags')
#         recipe = Recipe.objects.create(
#             author=request.user,
#             **validated_data
#         )
#         self.create_ingredients(recipe, ingredients)
#         recipe.tags.set(tags)
#         return recipe

#     def update(self, instance, validated_data):
#         ingredients = validated_data.pop('ingredients')
#         recipe = instance
#         RecipeIngredients.objects.filter(recipe_parent=recipe).delete()
#         self.create_ingredients(recipe, ingredients)
#         return super().update(recipe, validated_data)

#     def to_representation(self, instance):
#         return RecipeSerializer(
#             instance,
#             context={
#                 'request': self.context.get('request'),
#             }
#         ).data
