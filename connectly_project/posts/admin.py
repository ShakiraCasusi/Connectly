from django.contrib import admin

from .models import Post, Comment, Like, User, Follow
 
class UserAdmin(admin.ModelAdmin):
    """Customizes the display of the User model in the admin panel."""
    list_display = ('username', 'email', 'role', 'created_at')
    list_filter = ('role',)
    search_fields = ('username', 'email')
    list_per_page = 25
 
admin.site.register(User, UserAdmin)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Follow)