from rest_framework import serializers
from users.models import Author, Follows
from users.serializers import AuthorSerializer
import re
from django.core.exceptions import ValidationError


class FollowSerializer(serializers.Serializer):
    actor = AuthorSerializer(source='local_follower_id') 
    object = AuthorSerializer(source='followed_id') 

    class Meta:
        model = Follows
        fields = ['summary', 'actor', 'object']  # dont need 'type' because its checked in the view

    def create(self, validated_data):
        """
        Create and return a new Follows instance.
        """
        actor_data = validated_data.pop('local_follower_id')
        object_data = validated_data.pop('followed_id')
        #TODO: validate that the author id in the url is the same as the object's author id

        # Extract the UUID from the 'page' URL if 'id' is not present
        actor_id = self.extract_uuid_from_url(actor_data.get('page'))

        object_id = self.extract_uuid_from_url(object_data.get('page'))
    
        # Greg wants to follow lara 
        #local_follower = Author.objects.get(id=actor_data['id']) #Greg TODO: returns 500 if not found, maybe wanna return 404?
        #followed = Author.objects.get(id=object_data['id']) #Lara

        # Fetch the Author objects
        local_follower = Author.objects.get(id=actor_id)  # Get the follower
        followed = Author.objects.get(id=object_id)       # Get the followed author

        # Create the Follows object
        follows_instance = Follows.objects.create(
            local_follower_id=local_follower,
            followed_id=followed,
            status='PENDING',  #TODO: if they make a follow request but you're already following, what do you do?
            remote_follower_url=actor_data.get('remote_follower_url'),  # if applicable
            is_remote=False  #TODO: set is_remote by checking the host of follower (actor)
        )

        return follows_instance
    
    @staticmethod
    def extract_uuid_from_url(url):
        """
        Extracts UUID from the URL.
        """
        # Use regex to find the UUID pattern in the URL
        match = re.search(r'([0-9a-fA-F-]{36})', url)
        if not match:
            raise ValidationError("Invalid URL format, could not extract UUID")
        return match.group(1)
    

    