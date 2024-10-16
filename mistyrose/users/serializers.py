from rest_framework import serializers
from .models import Author, Post, Follows

class AuthorSerializer(serializers.Serializer):
    type = serializers.CharField(default='author', read_only=True)
    id = serializers.UUIDField()  # Full API URL for the author
    host = serializers.URLField() # The full API URL for the author's node
    displayName = serializers.CharField(source='display_name')
    github = serializers.URLField(required=False)  # URL of the user's GitHub
    profileImage = serializers.URLField(required=False, source='profile_image')
    page = serializers.URLField(required=False) 

    # Optional fields for public posts, followers, and following
    public_posts = serializers.SerializerMethodField(required=False)
    followers_count = serializers.SerializerMethodField(required=False)
    following_count = serializers.SerializerMethodField(required=False)


    # Get public posts for the author
    def get_public_posts(self, author):
        # Retrieve only public posts
        return PostSerializer(author.posts.filter(visibility='PUBLIC').order_by('-published'), many=True).data

    # Get count of followers for the author
    def get_followers_count(self, author):
        return Follows.objects.filter(followed_id=author, status='ACCEPTED').count()

    # Get count of authors the user is following
    def get_following_count(self, author):
        return Follows.objects.filter(local_follower_id=author, status='ACCEPTED').count()


    # https://dev.to/amanbothra/understanding-the-torepresentation-and-tointernalvalue-methods-in-the-django-rest-framework-naa 
    # get internal value for id - so we can pass the UUID for id instead of url
    def to_internal_value(self, data):
        id_url = data.pop('id', None)
        if id_url:
            author_id = id_url.rstrip('/').split('/')[-1] 
            data['id'] = author_id
        return super().to_internal_value(data)
    
    # https://dev.to/amanbothra/understanding-the-torepresentation-and-tointernalvalue-methods-in-the-django-rest-framework-naa want 'type' to be in serialized output but not part of model
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['type'] = 'author'  # Add 'type' to the representation
        return data
    