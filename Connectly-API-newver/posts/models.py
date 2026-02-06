from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.hashers import make_password
from django.db import models


'''
# Create your models here. - previous code
class User(models.Model):
    username = models.CharField(max_length=100, unique=True) #User's unique username
    password = models.CharField(max_length=128)  # Hashed password
    email = models.EmailField(unique=True) # User's unique email
    created_at = models.DateTimeField(auto_now_add=True) # Timestamp when the user was created

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'password']

    # The save method is overridden to hash the password using make_password before saving the user 
    # to the database. This ensures that the password is always stored securely.
    def save(self, *args, **kwargs):
        if not self.pk:  # Only hash the password on creation, not on updates
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
'''


class UserManager(BaseUserManager):
    def create_user(self, username, email, password, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username, email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):

    username = models.CharField(max_length=100, unique=True) # User's unique username
    password = models.CharField(max_length=128)  # Hashed password
    email = models.EmailField(unique=True) # User's unique email
    created_at = models.DateTimeField(auto_now_add=True) # Timestamp when the user was created
    is_staff = models.BooleanField(default=False) # For admin user
    is_active = models.BooleanField(default=True) # For activating the user

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'password']

    objects = UserManager()

    # The save method is overridden to hash the password using make_password before saving the user 
    # to the database. This ensures that the password is always stored securely.
    def save(self, *args, **kwargs):
        if not self.pk:  # Only hash the password on creation, not on updates
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


class Post(models.Model):
    content = models.TextField() # The text content of the post
    author = models.ForeignKey(User, on_delete=models.CASCADE) # The user who created the post
    created_at = models.DateTimeField(auto_now_add=True) # Timestamp when the post was created 

    def __str__(self):
        # return self.content[:50]
        return f"Post by {self.author.username} at {self.created_at}"
    
class Comment(models.Model):
    # text = models.TextField()
    content = models.TextField()
    author = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username} on Post {self.post.id}"
    
