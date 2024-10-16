from rest_framework import serializers
from users.models import Author, Follows
from users.serializers import AuthorSerializer


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

        # Greg wants to follow lara 
        local_follower = Author.objects.get(id=actor_data['id']) #Greg TODO: returns 500 if not found, maybe wanna return 404?
        followed = Author.objects.get(id=object_data['id']) #Lara

        # Create the Follows object
        follows_instance = Follows.objects.create(
            local_follower_id=local_follower,
            followed_id=followed,
            status='PENDING',  #TODO: if they make a follow request but you're already following, what do you do?
            remote_follower_url=actor_data.get('remote_follower_url'),  # if applicable
            is_remote=False  #TODO: set is_remote by checking the host of follower (actor)
        )

        return follows_instance