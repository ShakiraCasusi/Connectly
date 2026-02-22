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
    GoogleLogin,
)
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    # User endpoints
    path('users/', UserListCreate.as_view(), name='user-list-create'),

    # Post endpoints
    path('posts/', PostListCreate.as_view(), name='post-list-create'),
    path('posts/<int:pk>/', PostDetail.as_view(), name='post-detail'),
    path('posts/<int:pk>/like/', PostLike.as_view(), name='post-like'),
    path('posts/<int:pk>/comment/', PostCommentCreate.as_view(), name='post-comment-create'),
    path('posts/<int:pk>/comments/', PostCommentList.as_view(), name='post-comment-list'),

    # Comment endpoints
    path('comments/', CommentListCreate.as_view(), name='comment-list-create'),

    # Token auth endpoint
    path('token-auth/', obtain_auth_token, name='token-auth'),
    
    # Google OAuth endpoint
    path('auth/google/', GoogleLogin.as_view(), name='google-login'),

    # Debug endpoint para test auth
    path('test-auth/', TestAuth.as_view(), name='test-auth'),
]
