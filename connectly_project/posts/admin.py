from django.contrib import admin

from .models import Post, Comment, Like, User

admin.site.register(User)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Like)