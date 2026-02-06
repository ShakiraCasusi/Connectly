from django.urls import path
from .views import UserListCreate, PostListCreate, PostDetail, CommentListCreate
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    # Users
    path('users/', UserListCreate.as_view(), name='user-list-create'),

    # Posts
    path('posts/', PostListCreate.as_view(), name='post-list-create'),
    path('posts/<int:pk>/', PostDetail.as_view(), name='post-detail'),

    # Comments
    path('comments/', CommentListCreate.as_view(), name='comment-list-create'),

    # Token auth at root
    path('token-auth/', obtain_auth_token, name='token-auth'),
    
]
