from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView, ListCreateAPIView, UpdateAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from recipe.models import Recipe
from recipe.serializers import RecipeSerializer
from . import serializers

User = get_user_model()

class UserRegisterationAPIView(GenericAPIView):
    """
    An endpoint for clients to create a new user.
    """
    permission_classes = (AllowAny,)
    serializer_class = serializers.UserRegisterationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = RefreshToken.for_user(user)
        data = serializer.data
        data['tokens'] = {
            'refresh': str(token),
            'access': str(token.access_token)
        }
        return Response(data, status=status.HTTP_201_CREATED)


class UserLoginAPIView(GenericAPIView):
    """
    An endpoint to authenticate existing users using their email and password.
    """
    permission_classes = (AllowAny,)
    serializer_class = serializers.UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        response_data = serializers.CustomUserSerializer(user).data
        token = RefreshToken.for_user(user)
        response_data['tokens'] = {
            'refresh': str(token),
            'access': str(token.access_token)
        }
        return Response(response_data, status=status.HTTP_200_OK)


class UserLogoutAPIView(GenericAPIView):
    """
    An endpoint to log out users.
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"detail": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserAPIView(RetrieveUpdateAPIView):
    """
    Get and update user information.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.CustomUserSerializer

    def get_object(self):
        return self.request.user


class UserProfileAPIView(RetrieveUpdateAPIView):
    """
    Get and update user profile.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.ProfileSerializer

    def get_object(self):
        return self.request.user.profile


class UserAvatarAPIView(RetrieveUpdateAPIView):
    """
    Get and update user avatar.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.ProfileAvatarSerializer

    def get_object(self):
        return self.request.user.profile


class UserBookmarkAPIView(ListCreateAPIView):
    """
    Get, create, and delete favorite recipe bookmarks.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = RecipeSerializer

    def get_queryset(self):
        return self.request.user.profile.bookmarks.all()

    def post(self, request, *args, **kwargs):
        recipe_id = request.data.get('id')
        if not recipe_id:
            return Response({"detail": "Recipe ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        recipe = get_object_or_404(Recipe, id=recipe_id)
        user_profile = self.request.user.profile
        user_profile.bookmarks.add(recipe)
        return Response(status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        recipe_id = request.data.get('id')
        if not recipe_id:
            return Response({"detail": "Recipe ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=recipe_id)
        user_profile = self.request.user.profile
        user_profile.bookmarks.remove(recipe)
        return Response(status=status.HTTP_200_OK)


class PasswordChangeAPIView(UpdateAPIView):
    """
    Change password for authenticated users.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.PasswordChangeSerializer

    def get_object(self):
        return self.request.user
