from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import authenticate

class CustomAuthBackend(BaseBackend):

    def authenticate(self, request, username=None, password=None):
        
        user = authenticate(username=username, password=password)
        if user is not None:
            return user
        return None
