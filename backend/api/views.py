from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.models import Ingredient, Recipe, RecipeIngredients, Tag, User
from . import serializers


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.UserSerializer
    # permission_classes = (permissions.IsAdmin, )
    # filter_backends = (filters.SearchFilter, )
    # search_fields = ('=username', )
    # lookup_field = 'username'
    queryset = User.objects.all()

    @action(
        methods=('GET', ),
        detail=False,
        permission_classes=(IsAuthenticated, )
    )
    def me(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    @action(
        methods=('POST', ),
        detail=False,
        permission_classes=(IsAuthenticated, )
    )
    def set_password(self, request):
        serializer = serializers.PasswordSerializer(data=request.data)

        if serializer.is_valid():
            if not request.user.check_password(
                    serializer.data.get('current_password')):
                return Response({'current_password': ['Wrong password!']},
                                status=status.HTTP_400_BAD_REQUEST)
            request.user.set_password(serializer.data.get('new_password'))
            request.user.save()
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = serializers.RecipeSerializer
    permission_classes = (IsAuthenticated, )
    # pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


# class RecipeIngredientsViewSet(viewsets.ModelViewSet):
#     queryset = RecipeIngredients.objects.all()
#     serializer_class = serializers.RecipeIngredientsSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
    # permission_classes = (IsAuthenticated, )


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer
