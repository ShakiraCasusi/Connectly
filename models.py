from django.db import models


class User(models.Model):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("user", "User"),
        ("guest", "Guest"),
    )
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="user")

    # Add relations for following
    following = models.ManyToManyField(
        "self", symmetrical=False, related_name="followers", through="Follow"
    )

    def __str__(self):
        return self.username


class Post(models.Model):
    PRIVACY_CHOICES = (
        ("public", "Public"),
        ("private", "Private"),
    )
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    created_at = models.DateTimeField(auto_now_add=True)
    privacy = models.CharField(max_length=10, choices=PRIVACY_CHOICES, default="public")

    def __str__(self):
        return f"Post by {self.author.username} at {self.created_at}"


class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    created_at = models.DateTimeField(auto_now_add=True)


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)


class Follow(models.Model):
    follower = models.ForeignKey(User, related_name="following_relations", on_delete=models.CASCADE)
    followed = models.ForeignKey(User, related_name="follower_relations", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)