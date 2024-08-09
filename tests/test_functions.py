# This file is for functions that are not covered in api

import pytest
from recipe.models import get_default_recipe_category
from users.models import CustomUser

# create_user
@pytest.mark.django_db
def test_user_fail():
    with pytest.raises(ValueError) as exc_info:
        CustomUser.objects.create_user(username='testuser', email="", password='testpassword')
    assert str(exc_info.value) == "Users must have an email address"

# create_superuser
@pytest.mark.django_db
def test_create_superuser():
    with pytest.raises(ValueError) as exc_info:
        CustomUser.objects.create_superuser(username='testuser', email="user@example.com", password='testpassword', is_staff=False)
    assert str(exc_info.value) == "Superuser must have is_staff=True."
    with pytest.raises(ValueError) as exc_info:
        CustomUser.objects.create_superuser(username='testuser', email="user@example.com", password='testpassword', is_superuser=False)
    assert str(exc_info.value) == "Superuser must have is_superuser=True."

    response =  CustomUser.objects.create_superuser(username='testuser', email="user@example.com", password='testpassword', is_staff=True)
    assert response.username == "testuser"

# get_default_recipe_category
@pytest.mark.django_db
def test_get_default_recipe_category():
    response = get_default_recipe_category()
    assert response.name == "Others"