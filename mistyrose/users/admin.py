from django.contrib import admin
from .models import Author, Follows


admin.site.register(Author)
admin.site.register(Follows)