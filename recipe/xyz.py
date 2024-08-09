# recipes/tests.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient
from .models import Recipe

class RecipeAPITests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)  # Authenticate the client

        # Create a test recipe
        self.recipe = Recipe.objects.create(
            title='Test Recipe',
            ingredients='Test ingredients',
            instructions='Test instructions',
            author=self.user
        )
    
    def test_get_recipe_list(self):
        response = self.client.get(reverse('recipe-list'))  # Adjust URL name as necessary
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Expecting 1 recipe in the list

    def test_create_recipe(self):
        payload = {
            'title': 'New Recipe',
            'ingredients': 'New ingredients',
            'instructions': 'New instructions',
            'author': self.user.id
        }
        response = self.client.post(reverse('recipe-list'), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Recipe.objects.count(), 2)  # 1 existing + 1 new recipe
        self.assertEqual(Recipe.objects.latest('id').title, 'New Recipe')

    def test_update_recipe(self):
        payload = {
            'title': 'Updated Recipe',
            'ingredients': 'Updated ingredients',
            'instructions': 'Updated instructions'
        }
        response = self.client.put(reverse('recipe-detail', args=[self.recipe.id]), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.title, 'Updated Recipe')

    def test_delete_recipe(self):
        response = self.client.delete(reverse('recipe-detail', args=[self.recipe.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Recipe.objects.count(), 0)  # Recipe should be deleted

    def test_unauthorized_access(self):
        self.client.force_authenticate(user=None)  # Log out
        response = self.client.get(reverse('recipe-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_data(self):
        payload = {
            'title': '',  # Invalid data: title is required
            'ingredients': 'Some ingredients',
            'instructions': 'Some instructions'
        }
        response = self.client.post(reverse('recipe-list'), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
