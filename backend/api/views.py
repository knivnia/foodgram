from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from rest_framework import filters, mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from recipes.models import (Cart,
                            Favorite,
                            Ingredient,
                            Recipe,
                            RecipeIngredients,
                            Subscription,
                            Tag,
                            User)
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

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,),
        serializer_class=serializers.UserSerializer
    )
    def subscribe(self, request, pk):
        if request.method == 'POST':
            author = get_object_or_404(User, id=pk)
            if request.user == author:
                return Response({
                    'errors': 'Selfsubscription!'
                }, status=status.HTTP_400_BAD_REQUEST)
            if Subscription.objects.filter(
                    user=request.user,
                    author=author).exists():
                return Response(
                    'Already subscribed!',
                    status=status.HTTP_400_BAD_REQUEST)
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
        methods=['GET', ],
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        user = request.user
        queryset = Subscription.objects.filter(user=user)
        serializer = serializers.SubscriptionSerializer(
            queryset,
            many=True,
            context={'request': request}  # ????
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = serializers.RecipeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )
    # pagination_class = LimitOffsetPagination

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
        pdfmetrics.registerFont(
            TTFont('Georgia', 'Georgia.ttf', 'UTF-8'))
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = ('attachment; '
                                           'filename="shopping_list.pdf"')
        page = canvas.Canvas(response)
        page.setFont('Georgia', size=24)
        page.drawString(200, 800, 'Shopping list')
        page.setFont('Georgia', size=16)
        height = 750
        for i, (name, data) in enumerate(final_list.items(), 1):
            page.drawString(75, height, (f'{i}. {name} - {data["amount"]}, '
                                         f'{data["measurement_unit"]}'))
            height -= 25
        page.showPage()
        page.save()
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
                recipe=recipe
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
    permission_classes = (IsAuthenticated, )


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer
    permission_classes = (IsAuthenticated, )
