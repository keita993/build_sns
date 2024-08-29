from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from posts.models import Post

class PostModelTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.post = Post.objects.create(
            user=self.user,
            content='Test post content'
        )

    def test_post_content(self):
        post = Post.objects.get(id=1)
        expected_object_name = f'{post.content}'
        self.assertEqual(expected_object_name, 'Test post content')
class JWTAuthTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.token_obtain_url = reverse('token_obtain_pair')
        self.token_refresh_url = reverse('token_refresh')
        self.user_list_url = reverse('user-list')  # ユーザー一覧のURLを想定

    def test_obtain_token(self):
        response = self.client.post(self.token_obtain_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_refresh_token(self):
        # まず、トークンを取得
        response = self.client.post(self.token_obtain_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        refresh_token = response.data['refresh']

        # リフレッシュトークンを使用して新しいアクセストークンを取得
        response = self.client.post(self.token_refresh_url, {
            'refresh': refresh_token
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_access_protected_endpoint(self):
        # トークンを取得
        response = self.client.post(self.token_obtain_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        token = response.data['access']

        # 保護されたエンドポイントにアクセス
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(self.user_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_access_protected_endpoint_without_token(self):
        # トークンなしで保護されたエンドポイントにアクセス
        response = self.client.get(self.user_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)        