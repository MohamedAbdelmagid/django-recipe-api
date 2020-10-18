from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Ingredient
from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse("recipe:ingredient-list")


class PublicIngredientsApiTests(TestCase):
    """ Test the publicly available ingredients API """

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """ Test that login is required for retrieving ingredients """
        response = self.client.get(INGREDIENTS_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientTagsApiTests(TestCase):
    """ Test the authorized user ingredients API """

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            "test@gmail.com", "testpassword"
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """ Test retrieving ingredients """
        Ingredient.objects.create(user=self.user, name="Mustard Powder")
        Ingredient.objects.create(user=self.user, name="Red Chilli")

        response = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by("-name")
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """ Test that ingredients returned are for the authenticated user """
        user2 = get_user_model().objects.create_user("test2@gmail.com", "test2password")
        
        Ingredient.objects.create(user=user2, name="Onion Seeds")
        ingredient = Ingredient.objects.create(user=self.user, name="Kashmiri Mirch")

        response = self.client.get(INGREDIENTS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], ingredient.name)
