"""
URL configuration for connectly_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

# from ..posts.views import LoginView  # .. means back or up one level from current folder

urlpatterns = [
    path('admin/', admin.site.urls),    
    path('api-auth/', include('rest_framework.urls')), # DRF login/logout
    # -------^----- Navigate to http://127.0.0.1:8000/api-auth/login/ 
    # to see the DRF login interface. This confirms that DRF is installed and configured.
    path('posts/', include('posts.urls')),

    # workaround to test the requirement payload in page 3 of 5 of "Enabling HTTPS in Development"
    # see solution provided by AI from the following document: (argon2.md) argon2 challenges in installing:
    # path('login/', LoginView.as_view(), name='login-view'),  
]
