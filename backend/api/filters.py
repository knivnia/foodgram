import django_filters as filters

from recipes.models import Recipe, Ingredient


class IngredientSearchFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name', )


class RecipeFilter(filters.FilterSet):
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    author = filters.AllValuesMultipleFilter(field_name='author__id')

    class Meta:
        model = Recipe
        fields = [
            'tags',
            'author'
        ]
