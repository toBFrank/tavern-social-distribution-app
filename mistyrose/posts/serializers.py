from rest_framework import serializers
from .models import Post, Comment, Like

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = [
            'id',
            'author_id',
            'title',
            'description',
            'plain_or_markdown_content',
            'image_content',
            'content_type',
            'published',
            'visibility'
        ]
        
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