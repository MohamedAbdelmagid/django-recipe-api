from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPES_URL = reverse("recipe:recipe-list")


def recipe_url(recipe_id):
    """ Return recipe dtail URL """
    return reverse("recipe:recipe-detail", args=[recipe_id])


def sample_tag(user, name="Mutton Curry"):
    """ Create and return a sample tag """
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name="150 gms yogurt"):
    """ Create and return a sample ingredient """
    return Ingredient.objects.create(user=user, name=name)


def sample_recipe(user, **params):
    """ Create and return a sample recipe """
    defaults = {
        "name": "Sample Recipe",
        "cook_time": 15,
        "price": 10.00,
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTests(TestCase):
    """ Test unauthenticated recipe API access """

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """ Test that authentication is required """
        response = self.client.get(RECIPES_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """ Test unauthenticated recipe API access """

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@gmail.com", "testpassword"
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """ Test retrieving a list of recipes """
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        response = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by("-id")
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """ Test retrieving recipes for user """
        user2 = get_user_model().objects.create_user("test2@gmail.com", "test2password")
        sample_recipe(user=user2)
        sample_recipe(user=self.user)

        response = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data, serializer.data)

    def test_view_recipe_detail(self):
        """ Test viewing a recipe detail """
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = recipe_url(recipe.id)
        response = self.client.get(url)
        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(response.data, serializer.data)
