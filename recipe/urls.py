from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecipeViewSet, RecipeLikeViewSet

app_name = 'recipe'

router = DefaultRouter()
router.register(r'', RecipeViewSet, basename='recipe')

urlpatterns = [
    path('', include(router.urls)),
    path('create/', RecipeViewSet.as_view({'post': 'create_recipe'}), name='recipe-create'),
    path('<int:pk>/like/', RecipeLikeViewSet.as_view({'post': 'like', 'delete': 'unlike'}), name='recipe-like'),
]
