from rest_framework.permissions import BasePermission

# Only the post author can edit/delete their post
class IsPostAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user

# Admin-only access
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Admin').exists()
