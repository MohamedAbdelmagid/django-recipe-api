from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """ Test the users API (public) """

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_successful(self):
        """ Test creating user is successful """
        payload = {
            "email": "test@gmail.com",
            "password": "testpassword",
            "name": "Mohamed Abdelmagid",
        }
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**response.data)
        self.assertTrue(user.check_password(payload["password"]))
        self.assertNotIn("password", response.data)

    def test_user_exists(self):
        """ Test creating user that is already exists fails """
        payload = {
            "email": "test@gmail.com",
            "password": "testpassword",
            "name": "Mohamed Abdelmagid",
        }
        create_user(**payload)
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """ Test that the password must be more than 6 characters """
        payload = {
            "email": "test@gmail.com",
            "password": "test",
            "name": "Mohamed Abdelmagid",
        }
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(email=payload["email"]).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """ Test that a token is created for the user """
        payload = {
            "email": "test@gmail.com",
            "password": "testpassword",
            "name": "Mohamed Abdelmagid",
        }
        create_user(**payload)
        response = self.client.post(TOKEN_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)

    def test_create_token_invalid_credentials(self):
        """ Test that a token is created created for invalid credentials """
        payload = {
            "email": "test@gmail.com",
            "password": "testpassword",
            "name": "Mohamed Abdelmagid",
        }
        create_user(**payload)
        response = self.client.post(
            TOKEN_URL, {"email": "test@gmail.com", "password": "wrongpassword"}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", response.data)

    def test_create_token_no_user(self):
        """ Test that a token is not created if user doesn't exist """
        payload = {
            "email": "test@gmail.com",
            "password": "testpassword",
        }
        response = self.client.post(TOKEN_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", response.data)

    def test_create_token_missing_field(self):
        """ Test that email and password are provided """
        response1 = self.client.post(
            TOKEN_URL, {"email": "", "password": "testpassword"}
        )
        response2 = self.client.post(
            TOKEN_URL, {"email": "test@gmail.com", "password": ""}
        )

        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", response1.data)
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", response2.data)
