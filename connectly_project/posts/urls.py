from django.urls import path
from .views import (
    UserListCreate,
    PostListCreate,
    PostDetail,
    CommentListCreate,
    PostLike,
    PostCommentCreate,
    PostCommentList,
    TestAuth,
)
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    # Users
    path('users/', UserListCreate.as_view(), name='user-list-create'),

    # Posts
    path('posts/', PostListCreate.as_view(), name='post-list-create'),
    path('posts/<int:pk>/', PostDetail.as_view(), name='post-detail'),
    path('posts/<int:pk>/like/', PostLike.as_view(), name='post-like'),
    path('posts/<int:pk>/comment/', PostCommentCreate.as_view(), name='post-comment-create'),
    path('posts/<int:pk>/comments/', PostCommentList.as_view(), name='post-comment-list'),

    # Comments
    path('comments/', CommentListCreate.as_view(), name='comment-list-create'),

    # Token auth at root
    path('token-auth/', obtain_auth_token, name='token-auth'),
    
    # Test endpoint for debugging authentication
    path('test-auth/', TestAuth.as_view(), name='test-auth'),
]
