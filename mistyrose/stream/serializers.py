from rest_framework import serializers
from .models import Inbox

TYPE_CHOICES = [
      ('follow'),
      ('post'),
      ('comment'),
      ('like'),
    ]

class FollowSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=TYPE_CHOICES)
    summary = serializers.CharField(required=False)
    actor = AuthorSerializer() #TODO: import Author serializer
    object = AuthorSerializer() #TODO: import Author serializer