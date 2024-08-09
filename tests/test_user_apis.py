import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from users.models import CustomUser
from recipe.models import Recipe, RecipeCategory
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user():
    return CustomUser.objects.create_user(username='testuser', email="testuser@example.com", password='testpassword')

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

# GET /api/user/
@pytest.mark.django_db
def test_get_user_info(auth_client, user):
    url = reverse('users:user-info')
    response = auth_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['username'] == user.username

# PUT /api/user/
@pytest.mark.django_db
def test_update_user(auth_client):
    url = reverse('users:user-info')
    data = {'username': 'updateduser', 'email': 'updateduser@example.com'}
    response = auth_client.put(url, data)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['username'] == 'updateduser'
    assert response.data['email'] == 'updateduser@example.com'

# PATCH /api/user/
@pytest.mark.django_db
def test_patch_update_user(auth_client):
    url = reverse('users:user-info')
    data = {'email': 'patchupdate@example.com'}
    response = auth_client.patch(url, data)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['email'] == 'patchupdate@example.com'

# POST /api/user/login/
@pytest.mark.django_db
def test_user_login(api_client, user):
    url = reverse('users:login-user')
    data = {
        'email': user.email,
        'password': 'testpassword'
    }
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_200_OK
    assert 'access' in response.data["tokens"]
    assert 'refresh' in response.data["tokens"]

# POST /api/user/login/ - Faailure
@pytest.mark.django_db
def test_user_login_fail(api_client, user):
    url = reverse('users:login-user')
    data = {
        'email': user.email,
        'password': 'testpassword2'
    }
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

# POST /api/user/logout/
@pytest.mark.django_db
def test_user_logout(auth_client, api_client, user):
    login_url = reverse('users:login-user')
    url = reverse('users:logout-user')
    login_response = api_client.post(login_url, {'email': user.email, 'password': 'testpassword'})
    refresh_token = login_response.data['tokens']["refresh"]
    response = auth_client.post(url, {'refresh': refresh_token})
    assert response.status_code == status.HTTP_205_RESET_CONTENT

# POST /api/user/logout/ - Failure
@pytest.mark.django_db
def test_user_logout_fail(auth_client):
    url = reverse('users:logout-user')
    response = auth_client.post(url)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

# PUT /api/user/password/change/
@pytest.mark.django_db
def test_password_change(auth_client):
    url = reverse('users:change-password')
    data = {
        'old_password': 'testpassword',
        'new_password': 'newpassword123'
    }
    response = auth_client.put(url, data)
    assert response.status_code == status.HTTP_200_OK

# PUT /api/user/password/change/ - Failure
@pytest.mark.django_db
def test_password_change_fail(auth_client):
    url = reverse('users:change-password')
    data = {
        'old_password': 'testpasswo',
        'new_password': 'newpassword123'
    }
    response = auth_client.put(url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

# PATCH /api/user/password/change/
@pytest.mark.django_db
def test_password_change_patch(auth_client):
    url = reverse('users:change-password')
    data = {
        'old_password': 'testpassword',
        'new_password': 'newpassword123'
    }
    response = auth_client.patch(url, data)
    assert response.status_code == status.HTTP_200_OK

# GET /api/user/profile/
@pytest.mark.django_db
def test_get_user_profile(auth_client):
    url = reverse('users:user-profile')
    response = auth_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert 'bio' in response.data

# PUT /api/user/profile/
@pytest.mark.django_db
def test_update_user_profile(auth_client, recipe):
    url = reverse('users:user-profile')
    data = {"bookmarks": [recipe.id], "bio": "string"}
    response = auth_client.put(url, data)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['bio'] == 'string'

# PATCH /api/user/profile/
@pytest.mark.django_db
def test_partial_update_user_profile(auth_client):
    url = reverse('users:user-profile')
    data = {'bio': 'string11'}
    response = auth_client.patch(url, data)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['bio'] == 'string11'

# GET /api/user/profile/{id}/bookmarks/
@pytest.mark.django_db
def test_get_user_bookmarks(auth_client, user, recipe):
    url = reverse('users:user-bookmark', kwargs={'pk': user.id})
    data = {'id': recipe.id}
    response = auth_client.post(url, data)
    response = auth_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1

# POST /api/user/profile/{id}/bookmarks/
@pytest.mark.django_db
def test_create_user_bookmark(auth_client, recipe, user):
    url = reverse('users:user-bookmark', kwargs={'pk': user.id})
    data = {'id': recipe.id}
    response = auth_client.post(url, data)
    assert response.status_code == status.HTTP_200_OK

# DELETE /api/user/profile/{id}/bookmarks/
@pytest.mark.django_db
def test_delete_user_bookmark(auth_client, user, recipe):
    url = reverse('users:user-bookmark', kwargs={'pk':user.id})
    data = {'id': recipe.id}
    response = auth_client.delete(url, data)
    assert response.status_code == status.HTTP_200_OK

# GET /api/user/profile/avatar/
@pytest.mark.django_db
def test_get_user_avatar(auth_client):
    url = reverse('users:user-avatar')
    response = auth_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert 'avatar' in response.data

# PUT /api/user/profile/avatar/
@pytest.mark.django_db
def test_update_user_avatar(auth_client):
    url = reverse('users:user-avatar')

    image = Image.new('RGB', (100, 100), color = 'red')
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)

    avatar = SimpleUploadedFile("avatar.jpg", img_byte_arr.read(), content_type="image/jpeg")
    data = {'avatar': avatar}
    
    response = auth_client.put(url, data, format='multipart')
    assert response.status_code == status.HTTP_200_OK
    assert 'avatar' in response.data

# PATCH /api/user/profile/avatar/
@pytest.mark.django_db
def test_partial_update_user_avatar(auth_client):
    url = reverse('users:user-avatar')
    image = Image.new('RGB', (100, 100), color = 'red')
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)

    avatar = SimpleUploadedFile("avatar.jpg", img_byte_arr.read(), content_type="image/jpeg")
    data = {'avatar': avatar}
    response = auth_client.patch(url, data, format='multipart')
    assert response.status_code == status.HTTP_200_OK
    assert 'avatar' in response.data

# POST /api/user/register/
@pytest.mark.django_db
def test_user_registration(api_client):
    url = reverse('users:create-user')
    data = {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'newpassword'
    }
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_201_CREATED
    assert 'id' in response.data

# POST /api/user/token/refresh/
@pytest.mark.django_db
def test_token_refresh(api_client, user):
    login_url = reverse('users:login-user')
    refresh_url = reverse('users:token-refresh')
    login_response = api_client.post(login_url, {'email': user.email, 'password': 'testpassword'})
    refresh_token = login_response.data['tokens']["refresh"]
    response = api_client.post(refresh_url, {'refresh': refresh_token})
    assert response.status_code == status.HTTP_200_OK
    assert 'access' in response.data
