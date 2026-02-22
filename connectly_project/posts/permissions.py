from rest_framework.permissions import BasePermission

from .models import User as DomainUser

# Only the post author can edit or delete their own post
class IsPostAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        # obj.author is from posts.User, pero request.user is Django auth user when using TokenAuth
        # So kailangan natin compare by username para gumana together
        if isinstance(request.user, DomainUser):
            return obj.author_id == request.user.id

        username = getattr(request.user, 'username', None)
        if not username:
            return False

        domain_user = DomainUser.objects.filter(username=username).only('id').first()
        if not domain_user:
            return False

        return obj.author_id == domain_user.id

# Only admins can access
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Admin').exists()
