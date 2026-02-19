from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from .models import User as DomainUser, Post, Comment, Like


class LikesAndCommentsAPITests(APITestCase):
    def setUp(self):
        auth_user_model = get_user_model()

        # Auth user (used by TokenAuthentication)
        self.auth_user = auth_user_model.objects.create_user(
            username="alice",
            email="alice@example.com",
            password="Password123!",
        )
        self.token, _ = Token.objects.get_or_create(user=self.auth_user)

        # Matching domain user (used by Post/Comment/Like relations)
        self.domain_user = DomainUser.objects.create(
            username="alice",
            email="alice@example.com",
        )

        self.post = Post.objects.create(
            content="Hello world",
            author=self.domain_user,
        )

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_like_valid_post(self):
        res = self.client.post(f"/posts/posts/{self.post.id}/like/")
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data["post"], self.post.id)
        self.assertEqual(res.data["user"], self.domain_user.id)
        self.assertTrue(Like.objects.filter(user=self.domain_user, post=self.post).exists())

    def test_like_twice(self):
        self.client.post(f"/posts/posts/{self.post.id}/like/")
        res = self.client.post(f"/posts/posts/{self.post.id}/like/")
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.data, {"error": "Post already liked"})

    def test_like_missing_post(self):
        res = self.client.post("/posts/posts/999999/like/")
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.data, {"error": "Post not found"})

    def test_comment_valid_post(self):
        res = self.client.post(
            f"/posts/posts/{self.post.id}/comment/",
            data={"content": "Nice post!"},
            format="json",
        )
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data["content"], "Nice post!")
        self.assertEqual(res.data["author"], self.domain_user.id)
        self.assertEqual(res.data["post"], self.post.id)
        self.assertIn("created_at", res.data)

    def test_comment_empty_content(self):
        res = self.client.post(
            f"/posts/posts/{self.post.id}/comment/",
            data={"content": ""},
            format="json",
        )
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.data, {"error": "Content cannot be empty"})

    def test_comment_missing_post(self):
        res = self.client.post(
            "/posts/posts/999999/comment/",
            data={"content": "Hi"},
            format="json",
        )
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.data, {"error": "Post not found"})

    def test_get_comments_newest_first_with_pagination(self):
        Comment.objects.create(post=self.post, author=self.domain_user, text="First")
        Comment.objects.create(post=self.post, author=self.domain_user, text="Second")

        res = self.client.get(f"/posts/posts/{self.post.id}/comments/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("results", res.data)
        self.assertEqual(res.data["count"], 2)
        self.assertEqual(res.data["results"][0]["content"], "Second")
        self.assertEqual(res.data["results"][1]["content"], "First")

        # pagination page_size override
        for i in range(12):
            Comment.objects.create(post=self.post, author=self.domain_user, text=f"C{i}")

        res2 = self.client.get(f"/posts/posts/{self.post.id}/comments/?page=1&page_size=5")
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(len(res2.data["results"]), 5)
