from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecipeViewSet, RecipeLikeViewSet

app_name = 'recipe'

router = DefaultRouter()
# APIView is replaced by ViewSet here
router.register(r'', RecipeViewSet, basename='recipe')

urlpatterns = [
    path('', include(router.urls)),
    # This url is not necessary, just added so that application using `/create` api does not break
    path('create/', RecipeViewSet.as_view({'post': 'create_recipe'}), name='recipe-create'),
    # Api for likes dislikes
    path('<int:pk>/like/', RecipeLikeViewSet.as_view({'post': 'like', 'delete': 'unlike'}), name='recipe-like'),
]
