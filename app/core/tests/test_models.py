from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email="test@gmail.com", password="testpassword"):
    """ Create a sample user """
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):
    def test_create_user_with_email_successful(self):
        """ Test creating a new user with an email is successful """
        email = "mohamed.abdelmagid.1991@gmail.com"
        password = "testpassword1991"

        user = get_user_model().objects.create_user(email=email, password=password)
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """ Test the email for a new user is normalized """
        email = "mohamed.abdelmagid.1991@GMAIL.COM"
        user = get_user_model().objects.create_user(email, "testpassword1991")

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """ Test creating user no email raises error """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, "testpassword1991")

    def test_create_new_superuser(self):
        """ Test creating a new superuser """
        user = get_user_model().objects.create_superuser(
            "mohamed.abdelmagid.1991@gmail.com", "testpassword1991"
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """ Test the tag string representation """
        tag = models.Tag.objects.create(user=sample_user(), name="Soup")

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """ Test the ingredient string representation """
        ingredient = models.Ingredient.objects.create(
            user=sample_user(), name="Potatoes"
        )

        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        """ Test the recipe string representation """
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            name='Champaran Mutton Curry',
            cook_time=50,
            price=13.00
        )

        self.assertEqual(str(recipe), recipe.name)

    @patch("uuid.uuid4")
    def test_recipe_file_name_uuid(self, mock_uuid):
        """ Test that image is save in the right folder """
        uuid = "test-uuid"
        mock_uuid.return_value = uuid

        file_path = models.recipe_image_path(None, "image.jpg")
        path = "uploads/recipe/{uuid}.jpg".format(uuid=uuid)

        self.assertEqual(file_path, path)
