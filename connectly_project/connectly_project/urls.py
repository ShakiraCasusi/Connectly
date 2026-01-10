from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('posts/', include('posts.urls')),  # your posts API
]

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views  # add this

urlpatterns = [
    path('admin/', admin.site.urls),
    path('posts/', include('posts.urls')),  # your existing posts API
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),  # add this
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),  # add this
]

