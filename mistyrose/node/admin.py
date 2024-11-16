from django.contrib import admin

from .models import Node

class NodeAdmin(admin.ModelAdmin):
    list_display = ('name', 'host', 'is_whitelisted', 'is_authenticated')
    actions = ['connect_node', 'disconnect_node']

    def connect_node(self, request, queryset):
        for node in queryset:
            url = reverse('node-connect', kwargs={'pk': node.pk})
            HttpResponseRedirect(url)
    connect_node.short_description = "Test Connection for Selected Nodes"

    def disconnect_node(self, request, queryset):
        for node in queryset:
            node.is_whitelisted = False
            node.save()
        self.message_user(request, "Selected nodes have been disconnected.")
    disconnect_node.short_description = "Disconnect Selected Nodes"

admin.site.register(Node, NodeAdmin)
