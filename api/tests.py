from django.contrib.auth import SESSION_KEY, get_user_model
from rest_framework import status
from rest_framework.test import APITestCase


class LoginAPITests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="member@example.com",
            password="secure-password",
            user_type="Member",
        )
        self.url = "/api/login/"

    def test_login_returns_safe_user_data_and_creates_session(self):
        response = self.client.post(
            self.url,
            {"email": self.user.email, "password": "secure-password"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                "user": {
                    "id": self.user.pk,
                    "email": self.user.email,
                    "user_type": self.user.user_type,
                }
            },
        )
        self.assertNotIn("password", response.data["user"])
        self.assertEqual(
            str(self.client.session[SESSION_KEY]),
            str(self.user.pk),
        )

    def test_invalid_credentials_are_rejected(self):
        response = self.client.post(
            self.url,
            {"email": self.user.email, "password": "incorrect-password"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], "Invalid email or password.")


class RegistrationAPITests(APITestCase):
    def test_registration_returns_profile_without_an_avatar(self):
        response = self.client.post(
            "/api/register/",
            {
                "email": "new-member@example.com",
                "password": "secure-password",
                "password_confirm": "secure-password",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(response.data["user"]["profile"]["avatar"])
