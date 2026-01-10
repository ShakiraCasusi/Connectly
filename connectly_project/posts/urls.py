from django.urls import path
from .views import user_list, user_create, post_list, post_create

urlpatterns = [
    path('users/', user_list),
    path('users/create/', user_create),
    path('posts/', post_list),
    path('posts/create/', post_create),
]
