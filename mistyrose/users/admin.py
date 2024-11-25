from django.contrib import admin
from .models import Author, Follows

class AuthorAdmin(admin.ModelAdmin):
    readonly_fields = ('url',) #show url in django admin

# Register your models here.
admin.site.register(Author, AuthorAdmin)
admin.site.register(Follows)