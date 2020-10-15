from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model


class AdminSiteTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@gmail.com", password="adminpassword"
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email="mohamed.abdelmagid.1991@gmail.com",
            password="testpassword1991",
            name="Mohamed Abdemagid",
        )

    def test_users_listed(self):
        """ Test that users are listed on user page """
        url = reverse("admin:core_user_changelist")
        response = self.client.get(url)

        self.assertContains(response, self.user.name)
        self.assertContains(response, self.user.email)
