from django.contrib.auth.models import Group


def is_admin(user):
    return user.groups.filter(name='Admin').exists()

'''
you can import and use it in other parts of your Django project like this:

# your_app/views.py
from django.shortcuts import render
from .utils import is_admin

def some_view(request):
    if is_admin(request.user):
        # Do something for admin users
        pass
    else:
        # Do something for non-admin users
        pass
    return render(request, 'template.html')

'''