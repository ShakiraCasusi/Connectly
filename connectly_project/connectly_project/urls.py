from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.http import JsonResponse
from rest_framework.authtoken.views import obtain_auth_token  # import token view

# Root welcome page
def home(request):
    return JsonResponse({
        "message": "Welcome to Connectly API. Use /posts/users/ or /posts/posts/"
    })

urlpatterns = [
    path('', home),  # Root URL
    path('admin/', admin.site.urls),

    # API endpoints
    path('posts/', include('posts.urls')),  # all users, posts, comments endpoints

    # Web login/logout (optional)
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
]