from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from recipes.models import (Cart, Favorite, Ingredient, Recipe,
                            RecipeIngredients, Subscription, Tag)
from users.models import User
from . import serializers
from .utils import http2pdf
from .filters import IngredientSearchFilter, RecipeFilter


class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    pagination_class = PageNumberPagination

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
    )
    def subscribe(self, request, pk):
        if request.method == 'POST':
            author = get_object_or_404(User, id=pk)
            subscription = Subscription.objects.create(
                user=request.user,
                author=author
            )
            serializer = serializers.SubscriptionSerializer(
                subscription, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            subscription = get_object_or_404(
                Subscription,
                user=request.user,
                author_id=pk)
            subscription.delete()
            return Response(status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['GET'],
        pagination_class=PageNumberPagination
    )
    def subscriptions(self, request):
        page = self.paginate_queryset(
            Subscription.objects.filter(user=request.user))
        serializer = serializers.SubscriptionSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = serializers.RecipeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = RecipeFilter
    ordering = ('-pub_date',)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            if Cart.objects.filter(user=request.user, recipe_id=pk).exists():
                return Response(
                    'Recipe is already in the cart!',
                    status=status.HTTP_400_BAD_REQUEST)
            recipe = get_object_or_404(Recipe, id=pk)
            Cart.objects.create(
                user=request.user,
                recipe=recipe
            )
            serializer = serializers.ShortRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'DELETE':
            cart = get_object_or_404(Cart, recipe_id=pk)
            cart.delete()
            return Response(status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['GET', ],
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        final_list = {}
        ingredients = RecipeIngredients.objects.filter(
            recipe__cart__user=request.user).values_list(
            'ingredients__name', 'ingredients__measurement_unit',
            'amount')
        for item in ingredients:
            name = item[0]
            if name not in final_list:
                final_list[name] = {
                    'measurement_unit': item[1],
                    'amount': item[2]
                }
            else:
                final_list[name]['amount'] += item[2]
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = ('attachment; '
                                           'filename="shopping_list.pdf"')
        http2pdf(response, final_list)
        return response

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            if Favorite.objects.filter(
                    user=request.user,
                    recipe_id=pk).exists():
                return Response(
                    'Recipe is already favorite!',
                    status=status.HTTP_400_BAD_REQUEST)
            recipe = get_object_or_404(Recipe, id=pk)
            Favorite.objects.create(
                user=request.user,
                recipe_id=pk
            )
            serializer = serializers.ShortRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'DELETE':
            favorite = get_object_or_404(Favorite, recipe_id=pk)
            favorite.delete()
            return Response(status=status.HTTP_200_OK)


class RecipeIngredientsViewSet(viewsets.ModelViewSet):
    queryset = RecipeIngredients.objects.all()
    serializer_class = serializers.RecipeIngredientsSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = IngredientSearchFilter
    filterset_fields = ('name',)
    search_fields = ('^name',)
    ordering = ('id',)
    pagination_class = None


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer
    pagination_class = None
