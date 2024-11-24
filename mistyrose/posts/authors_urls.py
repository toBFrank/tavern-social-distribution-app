from django.urls import path
from .views import (
    AuthorPostsView,
    CommentedView, 
    CommentsView, 
    LikedView, 
    LikesView, 
    LikedCommentsView, 
    LikeView, 
    LikedFQIDView, 
    CommentRemoteByFQIDView, 
    CommentsByAuthorFQIDView, 
    CommentView,
    PostDetailsView,
    PostImageView)

"""
for post urls that start with api/authors/
"""
urlpatterns = [    
    # Post URLs
    path('<path:author_serial>/posts/<path:post_serial>/', PostDetailsView.as_view(), name='post-detail'),
    path('<path:author_serial>/posts/', AuthorPostsView.as_view(), name='author-posts'),
    path('<path:author_serial>/posts/<path:post_serial>/image/', PostImageView.as_view(), name='post-image'),
    
    # Comment URLs   
    path('<path:author_serial>/commented/', CommentedView.as_view(), name='commented'),
    path('<path:author_serial>/posts/<path:post_serial>/comments/', CommentsView.as_view(), name='get_post_comments'),
    path('<path:author_serial>/post/<path:post_serial>/comment/<path:comment_fqid>/', CommentRemoteByFQIDView.as_view(), name='get_remote_comment_fqid'),
    path('<path:author_fqid>/commented/', CommentsByAuthorFQIDView.as_view(), name='comments_by_author_fqid'),
    path('<path:author_serial>/commented/<path:comment_serial>/', CommentView.as_view(), name='comment'),

    # Like URLs
    path('<path:author_serial>/liked/', LikedView.as_view(), name='liked'),
    path('<path:author_serial>/liked/<path:like_serial>/', LikeView.as_view(), name='like'),
    path('<path:author_serial>/posts/<path:post_id>/likes/', LikesView.as_view(), name='post_likes'),
    path('<path:author_id>/posts/<path:post_id>/comments/<path:comment_id>/likes/', LikedCommentsView.as_view(), name='comment_likes'),
    path('<path:author_fqid>/liked/', LikedFQIDView.as_view(), name='liked_fqid'),
]
