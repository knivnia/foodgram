
from django.urls import include, path

from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

router.register(r'users', views.UserViewSet)
router.register(r'recipes', views.RecipeViewSet)
router.register(r'ingredients', views.IngredientViewSet)
router.register(r'tags', views.TagViewSet)

# router.register(
#     r'posts/(?P<post_id>.+)/comments',
#     views.CommentViewSet,
#     basename='Comment')
# router.register(r'follow', views.FollowViewSet, basename='Follow')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
