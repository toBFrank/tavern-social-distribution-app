from django.contrib import admin
from .models import Post, Comment, Like
from .models import Post, Like, Comment

# Register your models here.
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Like)
