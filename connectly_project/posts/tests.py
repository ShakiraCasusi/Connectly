from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from unittest.mock import patch

from .models import User as DomainUser, Post, Comment, Like, Follow


class LikesAndCommentsAPITests(APITestCase):
    def setUp(self):
        auth_user_model = get_user_model()

        # Auth user for TokenAuthentication
        self.auth_user = auth_user_model.objects.create_user(
            username="alice",
            email="alice@example.com",
            password="Password123!",
        )
        self.token, _ = Token.objects.get_or_create(user=self.auth_user)

        # Domain user for Post/Comment/Like relations
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

        # Can also specify page_size in the URL
        for i in range(12):
            Comment.objects.create(post=self.post, author=self.domain_user, text=f"C{i}")

        res2 = self.client.get(f"/posts/posts/{self.post.id}/comments/?page=1&page_size=5")
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(len(res2.data["results"]), 5)


class GoogleLoginAPITests(APITestCase):
    def setUp(self):
        self.auth_user_model = get_user_model()

    @patch('posts.views.id_token.verify_oauth2_token')
    def test_google_login_success_new_user(self, mock_verify_token):
        """Test successful login and user creation for a new Google user."""
        # Simulate a valid Google token verification
        mock_verify_token.return_value = {
            'email': 'new.user@gmail.com',
            'name': 'New User',
        }

        res = self.client.post("/posts/auth/google/", data={"id_token": "fake-token"}, format="json")

        self.assertEqual(res.status_code, 200)
        self.assertIn("token", res.data)
        self.assertEqual(res.data["email"], "new.user@gmail.com")

        # Verify users were created in both tables
        self.assertTrue(self.auth_user_model.objects.filter(email="new.user@gmail.com").exists())
        self.assertTrue(DomainUser.objects.filter(email="new.user@gmail.com").exists())

    @patch('posts.views.id_token.verify_oauth2_token')
    def test_google_login_success_existing_user(self, mock_verify_token):
        """Test successful login for an existing user."""
        # Pre-create the user
        user = self.auth_user_model.objects.create_user(username="jane", email="jane.doe@gmail.com", password="pw")
        DomainUser.objects.create(username="jane", email="jane.doe@gmail.com")

        mock_verify_token.return_value = {'email': 'jane.doe@gmail.com'}

        res = self.client.post("/posts/auth/google/", data={"id_token": "fake-token"}, format="json")

        self.assertEqual(res.status_code, 200)
        self.assertIn("token", res.data)
        self.assertEqual(res.data["email"], "jane.doe@gmail.com")

        # Verify no new user was created
        self.assertEqual(self.auth_user_model.objects.count(), 1)
        self.assertEqual(DomainUser.objects.count(), 1)

    @patch('posts.views.id_token.verify_oauth2_token')
    def test_google_login_invalid_token(self, mock_verify_token):
        """Test login failure with an invalid token."""
        mock_verify_token.side_effect = ValueError("Token is invalid")

        res = self.client.post("/posts/auth/google/", data={"id_token": "invalid-token"}, format="json")

        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.data, {"error": "Token verification failed: Token is invalid"})

    def test_google_login_missing_token(self):
        """Test login failure when id_token is not provided."""
        res = self.client.post("/posts/auth/google/", data={}, format="json")

        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.data, {"error": "Missing id_token"})


class FeedAPITests(APITestCase):
    def setUp(self):
        # #squad up
        auth_user_model = get_user_model()

        # User 1: The one making the request
        self.user1_auth = auth_user_model.objects.create_user(username="user1", password="pw")
        self.user1_domain = DomainUser.objects.create(username="user1")
        self.token1, _ = Token.objects.get_or_create(user=self.user1_auth)

        # User 2: The user that user1 will follow
        self.user2_auth = auth_user_model.objects.create_user(username="user2", password="pw")
        self.user2_domain = DomainUser.objects.create(username="user2")

        # User 3: A random user that user1 does not follow
        self.user3_auth = auth_user_model.objects.create_user(username="user3", password="pw")
        self.user3_domain = DomainUser.objects.create(username="user3")

        # Create some posts
        self.post_by_user1 = Post.objects.create(author=self.user1_domain, content="My own post")
        self.post_by_user2 = Post.objects.create(author=self.user2_domain, content="A post from someone I follow")
        self.post_by_user3 = Post.objects.create(author=self.user3_domain, content="A post from a stranger")

        # User1 follows User2
        Follow.objects.create(follower=self.user1_domain, followed=self.user2_domain)

        # Authenticate as user1
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token1.key}")

    def test_get_global_feed(self):
        """
        Tests the default feed, which should return all posts.
        """
        res = self.client.get("/posts/feed/")
        self.assertEqual(res.status_code, 200)

        # Should contain all 3 posts
        self.assertEqual(res.data['count'], 3)
        
        # Check content of posts to be sure
        contents = {item['content'] for item in res.data['results']}
        self.assertIn("My own post", contents)
        self.assertIn("A post from someone I follow", contents)
        self.assertIn("A post from a stranger", contents)

    def test_get_following_feed(self):
        """
        Tests the filtered feed, which should return posts from followed users
        and the user's own posts.
        """
        res = self.client.get("/posts/feed/?filter=following")
        self.assertEqual(res.status_code, 200)

        # Should contain 2 posts: one from user1 (self) and one from user2 (followed)
        self.assertEqual(res.data['count'], 2)
        contents = {item['content'] for item in res.data['results']}
        self.assertIn("My own post", contents)
        self.assertIn("A post from someone I follow", contents)
        self.assertNotIn("A post from a stranger", contents)
