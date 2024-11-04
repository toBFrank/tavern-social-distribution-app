from mistyrose.users.serializers import AuthorSerializer
from rest_framework import serializers
from .models import Post, Comment, Like

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

#region Post Serializers
class PostSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(source='author_id')
    comments = CommentSerializer(many=True, read_only=True)
    likes = LikeSerializer(many=True, read_only=True)
    # likes_count = serializers.SerializerMethodField()  # Add likes count
    # comments_count = serializers.SerializerMethodField()  # Add comments count
    class Meta:
        model = Post
        fields = [
            'type',
            'title',
            'id',
            'description', 
            'content_type',
            'content',
            'author',
            'comments',
            'likes',
            'published',
            'visibility'
        ]

        # Method to get likes count for a post
    def get_likes_count(self, post):
        return Like.objects.filter(object_id=post.id).count()

    # Method to get comments count for a post
    def get_comments_count(self, post):
        return Comment.objects.filter(post_id=post.id).count()


#endregion