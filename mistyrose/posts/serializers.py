from rest_framework import serializers
from .models import Post, Comment, Like
# from users.serializers import AuthorSerializer #TODO:uncomment after Author Serializer fix
import importlib
from django.urls import reverse

#TODO: remove - this is a temporary fix for the circular dependency issue in Authors which is importing PostSerializer
def get_author_serializer():
    users_serializers = importlib.import_module("users.serializers")
    return users_serializers.AuthorSerializer


#region Post Serializers
class PostSerializer(serializers.ModelSerializer):
    likes_count = serializers.SerializerMethodField()  # Add likes count
    comments_count = serializers.SerializerMethodField()  # Add comments count
    class Meta:
        model = Post
        fields = [
            'id',
            'author_id',
            'title',
            'description',
            'text_content',
            'image_content',
            'content_type',
            'published',
            'visibility',
            'likes_count', 
            'comments_count'  
        ]
   
        read_only_fields = [
            'id',
            'published', 
        ]
        # Method to get likes count for a post
    def get_likes_count(self, post):
        return Like.objects.filter(object_id=post.id).count()

    # Method to get comments count for a post
    def get_comments_count(self, post):
        return Comment.objects.filter(post_id=post.id).count()


#endregion

#region Comment Serializers        
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            'id',
            'author_id',
            'published',
            'comment',
            'post_id',
            'content_type',
            'page'
        ]
#endregion
        
#region Like Serializers
class LikeSerializer(serializers.ModelSerializer):
    type = serializers.CharField(default='like', read_only=True)
    author = serializers.SerializerMethodField()
    # author = AuthorSerializer(source='author_id')  #TODO: uncomment after Author serializer issue is fixed
    object = serializers.SerializerMethodField() # calls get_object with current Like instance -> method will get the object_url
    id = serializers.SerializerMethodField()
    class Meta:
        model = Like
        fields = [
            'type',
            'author',
            'published',
            'id',
            'object',
        ]

    #asked chatGPT how to set the host in the serializer, need to send context from the view and call it as shown 2024-11-02
    def get_id(self, like_object): #get is for turning into JSON response
        author_host = like_object.author_id.host.rstrip('/')
        return f"{author_host}/authors/{like_object.author_id.id}/liked/{like_object.id}"


    def get_object(self, like_object):
        return like_object.object_url
    
    def get_author(self, like_object): #TODO: remove - this is temporary fix to circular dependency in AuthorSerializer importing PostSerializer
        AuthorSerializer = get_author_serializer()
        return AuthorSerializer(like_object.author_id).data

#endregion