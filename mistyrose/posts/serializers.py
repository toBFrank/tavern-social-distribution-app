from rest_framework import serializers
from .models import Post, Comment, Like

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
            'published'
        ]
        # Method to get likes count for a post
    def get_likes_count(self, post):
        return Like.objects.filter(object_url=post.id).count()

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
    class Meta:
        model = Like
        fields = [
            'id',
            'author_id',
            'published',
            'object_url'
        ]
#endregion