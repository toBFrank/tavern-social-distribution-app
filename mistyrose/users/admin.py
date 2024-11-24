from django.contrib import admin
from .models import Author, Follows

class AuthorAdmin(admin.ModelAdmin):
    readonly_fields = ('url',) #show url in django admin

class FollowsAdmin(admin.ModelAdmin):
    list_display = ('local_follower_id', 'remote_follower_url', 'followed_id', 'status', 'is_remote')

# Register your models here.
admin.site.register(Author, AuthorAdmin)
admin.site.register(Follows, FollowsAdmin)