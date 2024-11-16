from django.contrib import admin
from .models import Node

admin.site.unregister(Node)
admin.site.register(Node)
