from rest_framework import serializers
from .models import User, Post, Comment

# -------------------------
# User Serializer
# -------------------------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'created_at']
        read_only_fields = ['id', 'created_at']

# -------------------------
# Post Serializer
# -------------------------
class PostSerializer(serializers.ModelSerializer):
    # Use PK related field to allow assigning request.user
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    comments = serializers.SerializerMethodField()  # nested comments

    class Meta:
        model = Post
        fields = ['id', 'content', 'author', 'created_at', 'comments']
        read_only_fields = ['id', 'author', 'created_at', 'comments']

    def get_comments(self, obj):
        comments = obj.comments.all()
        return CommentSerializer(comments, many=True).data

# -------------------------
# Comment Serializer
# -------------------------
class CommentSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())

    class Meta:
        model = Comment
        fields = ['id', 'text', 'author', 'post', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']
