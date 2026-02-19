from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from .models import User, Post, Comment, Like


# User Serializer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserCreateSerializer(serializers.Serializer):
    """
    Creates BOTH:
    - a Django auth user (used by DRF TokenAuthentication / token-auth endpoint)
    - a domain user profile in posts.User (used by Post/Comment/Like relations)

    This keeps existing architecture intact while making token auth usable.
    """

    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_username(self, value):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Username cannot be empty")
        return value

    def validate_password(self, value):
        if not (value or "").strip():
            raise serializers.ValidationError("Password cannot be empty")
        return value

    @transaction.atomic
    def create(self, validated_data):
        auth_user_model = get_user_model()
        username = validated_data['username']
        email = validated_data['email']
        password = validated_data['password']

        # Create or validate the Django auth user
        if auth_user_model.objects.filter(username=username).exists():
            raise serializers.ValidationError({"error": "Username already exists"})

        auth_user = auth_user_model.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        Token.objects.get_or_create(user=auth_user)

        # Create matching domain profile user
        domain_user = User.objects.create(username=username, email=email)
        return domain_user


# Post Serializer

class PostSerializer(serializers.ModelSerializer):
    # Use PK related field to allow assigning request.user
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    comments = serializers.SerializerMethodField()  # nested comments
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'content', 'author', 'created_at', 'comments', 'like_count', 'comment_count']
        read_only_fields = ['id', 'author', 'created_at', 'comments', 'like_count', 'comment_count']

    def get_comments(self, obj):
        comments = obj.comments.order_by('-created_at')
        return CommentSerializer(comments, many=True).data

    def get_like_count(self, obj):
        # related_name='likes' on Like.post
        return obj.likes.count()

    def get_comment_count(self, obj):
        return obj.comments.count()


# Comment Serializer

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())

    class Meta:
        model = Comment
        fields = ['id', 'text', 'author', 'post', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']

    def validate_text(self, value):
        if not (value or "").strip():
            raise serializers.ValidationError("Content cannot be empty")
        return value


class PostCommentCreateSerializer(serializers.Serializer):
    content = serializers.CharField(allow_blank=True)

    def validate_content(self, value):
        if not (value or "").strip():
            raise serializers.ValidationError("Content cannot be empty")
        return value


class PostCommentSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    post = serializers.PrimaryKeyRelatedField(read_only=True)
    content = serializers.CharField(source='text', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'content', 'author', 'post', 'created_at']
        read_only_fields = ['id', 'content', 'author', 'post', 'created_at']


class LikeSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    post = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Like
        fields = ['id', 'user', 'post', 'created_at']
        read_only_fields = ['id', 'user', 'post', 'created_at']
