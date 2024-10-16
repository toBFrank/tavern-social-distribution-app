from django.contrib import admin

from .models import Node
class NodeAdmin(admin.ModelAdmin):
    model = Node
    list_display = ('host', 'username', 'password', 'team')
    list_display_links = None
    list_editable = ('host', 'username', 'password', 'team')
    list_filter = ('host',)
    search_fields = ('host', 'username')
    ordering = ('host',)
    
admin.site.register(Node)
