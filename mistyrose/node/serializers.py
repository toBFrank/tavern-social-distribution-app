from rest_framework import serializers
from .models import Node

class NodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Node
        fields = ("host", "username", "is_whitelisted", "is_authenticated")
        extra_kwargs = {
            "username": {"write_only": True},
            "password": {"write_only": True}
        }