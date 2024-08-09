from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Recipe, RecipeLike
from .serializers import RecipeSerializer
from .permissions import IsAuthorOrReadOnly

class RecipeViewSet(viewsets.ModelViewSet):
    """
    Recipe ViewSet for viewing, creating, updating, and deleting recipes.
    """
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def get_permissions(self):
        if self.action in ['list', "retrieve"]:
            return [AllowAny()]
        elif self.action in ['create', "create_recipe"]:
            return [IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthorOrReadOnly()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=False, methods=['post'], url_path='create', permission_classes=[IsAuthenticated])
    def create_recipe(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class RecipeLikeViewSet(viewsets.ViewSet):
    """
    Like, Dislike a recipe
    """
    @action(detail=True, methods=['post'], url_path='like', permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        new_like, created = RecipeLike.objects.get_or_create(user=request.user, recipe=recipe)
        if created:
            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='like', permission_classes=[IsAuthenticated])
    def unlike(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        like = RecipeLike.objects.filter(user=request.user, recipe=recipe)
        if like.exists():
            like.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)