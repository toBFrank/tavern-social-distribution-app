from rest_framework import serializers
from posts.serializers import PostSerializer
from users.models import Author,Follows
from posts.models import Post,Like,Comment

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
    friends_posts = serializers.SerializerMethodField(required=False)
    unlisted_posts = serializers.SerializerMethodField(required=False)
    followers_count = serializers.SerializerMethodField(required=False)
    following_count = serializers.SerializerMethodField(required=False)
    #likes_count = serializers.SerializerMethodField(required=False)
    #comments_count = serializers.SerializerMethodField(required=False)


     # Get public posts for the author
    def get_public_posts(self, author):
        # Retrieve only public posts
        return PostSerializer(author.posts.filter(visibility='PUBLIC').order_by('-published'), many=True).data
    
    # Get all friends posts for the author
    def get_friends_posts(self, author):
        return PostSerializer(author.posts.filter(visibility='FRIENDS').order_by('-published'), many=True).data

    # Get all unlisted posts for the author
    def get_unlisted_posts(self, author):
        return PostSerializer(author.posts.filter(visibility='UNLISTED').order_by('-published'), many=True).data


    # Get count of followers for the author
    def get_followers_count(self, author):
        return Follows.objects.filter(followed_id=author, status='ACCEPTED').count()

    # Get count of authors the user is following
    def get_following_count(self, author):
        return Follows.objects.filter(local_follower_id=author, status='ACCEPTED').count()
    
    # Get the count of likes on all posts by the author
    #def get_likes_count(self, author):
        # Find all posts by the author, then count likes related to those posts
        #return Like.objects.filter(object_url__in=author.posts.values_list('id', flat=True)).count()

    # Get count of comments on all posts by the author
    #def get_comments_count(self, author):
        # Find all posts by the author, then count comments related to those posts
        #return Comment.objects.filter(post_id__in=author.posts.values_list('id', flat=True)).count()


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

        # Remove fields if they are empty or None to prevent error in follow requests with empty string fields
        if not data.get('github'):
            data.pop('github', None)
        if not data.get('profileImage'):
            data.pop('profileImage', None)
        return data
    
class AuthorEditProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['display_name', 'github', 'profile_image']  # Only fields you want to update
    
    def update(self, instance, validated_data):
        # Update the author instance with the provided validated data
        instance.display_name = validated_data.get('display_name', instance.display_name)
        instance.github = validated_data.get('github', instance.github)
        instance.profile_image = validated_data.get('profile_image', instance.profile_image)
        instance.save()  # Save the updated instance to the database
        return instance

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    