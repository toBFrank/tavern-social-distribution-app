from rest_framework import serializers
from .models import Post, Comment, Like

#region Post Serializers
class PostSerializer(serializers.ModelSerializer):
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
            'visibility'
        ]
        read_only_fields = [
            'id',
            'published'
        ]
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
            'content_type',
            'object_id',
        ]
#endregion