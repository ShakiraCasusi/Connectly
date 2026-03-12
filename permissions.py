from rest_framework import permissions
from .models import User as DomainUser


def _get_domain_user_from_auth(auth_user):
    """Helper function to get the domain user from the request.user (AuthUser)."""
    if not auth_user or not auth_user.is_authenticated:
        return None
    try:
        return DomainUser.objects.get(username=auth_user.username)
    except DomainUser.DoesNotExist:
        return None


class IsAdmin(permissions.BasePermission):
    """
    Custom permission to only allow users with 'admin' role.
    """

    def has_permission(self, request, view):
        domain_user = _get_domain_user_from_auth(request.user)
        return domain_user and domain_user.role == "admin"


class IsPostAuthor(permissions.BasePermission):
    """Object-level permission to only allow owners of a post to edit it."""

    def has_object_permission(self, request, view, obj):
        domain_user = _get_domain_user_from_auth(request.user)
        return obj.author == domain_user