from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class AuthTests(APITestCase):
    def test_register_and_token(self):
        register_url = reverse("register")
        response = self.client.post(
            register_url,
            {"username": "demo", "email": "demo@example.com", "password": "demo1234"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        token_url = reverse("token_obtain_pair")
        response = self.client.post(
            token_url, {"username": "demo", "password": "demo1234"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)


class VideoTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="video_user", password="video1234"
        )

    def test_list_videos_public(self):
        response = self.client.get("/api/videos/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
