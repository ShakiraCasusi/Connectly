from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.http import JsonResponse
from rest_framework.authtoken.views import obtain_auth_token  # for API token auth

# Home page endpoint
def home(request):
    return JsonResponse({
        "message": "Welcome to Connectly API. Use /posts/users/ or /posts/posts/"
    })

urlpatterns = [
    path('', home),  # Home endpoint
    path('admin/', admin.site.urls),

    # Main API routes
    path('posts/', include('posts.urls')),  # posts module has all the API endpoints

    # Login/logout pages (optional if needed)
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
]