from django.db import models


class User(models.Model):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("user", "User"),
        ("guest", "Guest"),
    )
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="user")


    def __str__(self):
        return self.username


class Post(models.Model):
    PRIVACY_CHOICES = (
        ("public", "Public"),
        ("private", "Private"),
    )
    content = models.TextField()
    author = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    privacy = models.CharField(max_length=10, choices=PRIVACY_CHOICES, default="public")


    def __str__(self):
        return f"Post by {self.author.username} at {self.created_at}"


class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Comment by {self.author.username} on Post {self.post.id}"


class Like(models.Model):
    user = models.ForeignKey(User, related_name='likes', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='likes', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'post'], name='unique_user_post_like')
        ]

    def __str__(self):
        return f"Like by {self.user.username} on Post {self.post.id}"


class Follow(models.Model):
    """
    Represents a user following another user.
    """
    # The user doing the following
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    # The user being followed
    followed = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # A user can't follow the same person twice
        unique_together = ('follower', 'followed')