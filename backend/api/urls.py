from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

router.register('users', views.UserViewSet)
router.register('recipes', views.RecipeViewSet)
router.register('ingredients', views.IngredientViewSet)
router.register('tags', views.TagViewSet)

urlpatterns = [
    path('users/subscriptions/', views.UserViewSet.as_view(
        {'get': 'subscriptions'})
    ),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls')),
    path('', include(router.urls)),
]
