import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from recipe.models import Recipe, RecipeCategory
from users.models import CustomUser
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user():
    user = CustomUser.objects.create_user(username='testuser', email="testuser#example.com", password='testpassword')
    return user

@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client

@pytest.fixture
def category():
    return RecipeCategory.objects.create(name='category1')

@pytest.fixture
def recipe(category, user):
    return Recipe.objects.create(
        author=user,
        category=category,
        title='Init Recipe',
        desc='Init description',
        cook_time='01:00:00',
        ingredients='item1, item2',
        procedure='procedure1'
    )

# GET /api/recipe/
@pytest.mark.django_db
def test_get_recipe_list(auth_client, recipe):
    response = auth_client.get(reverse('recipe:recipe-list'), {
        'category__name': recipe.category.name,
        'author__username': recipe.author.username
    })
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1

# POST /api/recipe/
@pytest.mark.django_db
def test_post_recipe(auth_client, category):
    image = Image.new('RGB', (100, 100), color = 'red')
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)

    picture = SimpleUploadedFile("image.jpg", img_byte_arr.read(), content_type="image/jpeg")
    payload = {
        'category.name': category.name,
        'title': 'New Recipe',
        'desc': 'New description',
        'cook_time': '01:30:00',
        'ingredients': 'Ingredients',
        'procedure': 'Procedure',
        'picture': picture
    }
    response = auth_client.post(reverse('recipe:recipe-list'), payload, format='multipart')
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["category_name"] == category.name

# GET /api/recipe/{id}/
@pytest.mark.django_db
def test_get_recipe_detail(auth_client, recipe):
    response = auth_client.get(reverse('recipe:recipe-detail', args=[recipe.id]))
    assert response.status_code == status.HTTP_200_OK
    assert response.data['title'] == 'Init Recipe'

# PUT /api/recipe/{id}/
@pytest.mark.django_db
def test_put_recipe(auth_client, recipe, category):
    image = Image.new('RGB', (100, 100), color = 'red')
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)

    picture = SimpleUploadedFile("image.jpg", img_byte_arr.read(), content_type="image/jpeg")

    payload = {
        'title': 'Updated Recipe',
        'desc': 'Updated description',
        'cook_time': '02:00:00',
        'ingredients': 'item1, item2',
        'procedure': 'procedure1',
        'category.name': category.name,
        'picture': picture
    }
    response = auth_client.put(reverse('recipe:recipe-detail', args=[recipe.id]), data=payload, format="multipart")
    assert response.status_code == status.HTTP_200_OK
    recipe.refresh_from_db()
    assert recipe.title == 'Updated Recipe'

# PATCH /api/recipe/{id}/
@pytest.mark.django_db
def test_patch_recipe(auth_client, recipe):
    payload = {'desc': 'Partially updated description'}
    response = auth_client.patch(reverse('recipe:recipe-detail', args=[recipe.id]), payload, format='json')
    assert response.status_code == status.HTTP_200_OK
    recipe.refresh_from_db()
    assert recipe.desc == 'Partially updated description'

# DELETE /api/recipe/{id}/
@pytest.mark.django_db
def test_delete_recipe(auth_client, recipe):
    response = auth_client.delete(reverse('recipe:recipe-detail', args=[recipe.id]))
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Recipe.objects.count() == 0

# POST /api/recipe/{id}/like/
@pytest.mark.django_db
def test_post_recipe_like(auth_client, recipe):
    response = auth_client.post(reverse('recipe:recipe-like', args=[recipe.id]))
    assert response.status_code == status.HTTP_201_CREATED
    assert recipe.get_total_number_of_likes() == 1

# POST /api/recipe/{id}/like/ - Fail
@pytest.mark.django_db
def test_post_recipe_like_fail(auth_client, recipe):
    url = reverse('recipe:recipe-like', args=[recipe.id])
    auth_client.post(url)
    response = auth_client.post(url)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

# DELETE /api/recipe/{id}/like/
@pytest.mark.django_db
def test_delete_recipe_like(auth_client, recipe):
    auth_client.post(reverse('recipe:recipe-like',  kwargs={'pk': recipe.id}))
    response = auth_client.delete(reverse('recipe:recipe-like', kwargs={'pk': recipe.id}))
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert recipe.get_total_number_of_likes() == 0

# DELETE /api/recipe/{id}/like/ - Failure
@pytest.mark.django_db
def test_delete_recipe_like_fail(auth_client, recipe):
    response = auth_client.delete(reverse('recipe:recipe-like', kwargs={'pk': recipe.id}))
    assert response.status_code == status.HTTP_400_BAD_REQUEST

# POST /api/recipe/create/
@pytest.mark.django_db
def test_post_create_recipe(auth_client, category):
    image = Image.new('RGB', (100, 100), color = 'red')
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)

    picture = SimpleUploadedFile("image.jpg", img_byte_arr.read(), content_type="image/jpeg")
    payload = {
        'category.name': category.name,
        'title': 'New Recipe',
        'desc': 'New description',
        'cook_time': '01:30:00',
        'ingredients': 'Ingredients',
        'procedure': 'Procedure',
        'picture': picture
    }
    response = auth_client.post(reverse('recipe:recipe-create'), payload, format='multipart')
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["category_name"] == category.name

# POST /api/recipe/create/ - Failure
@pytest.mark.django_db
def test_post_create_recipe_fail(auth_client, category):
    payload = {
        'category.name': category.name,
        'title': 'New Recipe',
        'desc': 'New description',
        'cook_time': '01:30:00',
        'ingredients': 'Ingredients',
        'procedure': 'Procedure',
        'picture': "xyz"
    }
    response = auth_client.post(reverse('recipe:recipe-create'), payload, format='multipart')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
