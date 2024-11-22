from rest_framework import serializers
from .models import Node

class NodeSerializer(serializers.ModelSerializer):
    host = serializers.URLField(source='remote_node_url', required=True)
    username = serializers.CharField(source='remote_username', required=True)
    password = serializers.CharField(source='remote_password', required=True)
    
    class Meta:
        model = Node
        fields = [
            'host',
            'username',
            'password',
        ]
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return {
            'host': representation['host'],
            'username': representation['username'],
            'password': representation['password'],
        }