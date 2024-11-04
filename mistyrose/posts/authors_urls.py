from django.urls import path
from .views import CommentedView, CommentsView, LikedView, LikesView, LikedCommentsView, LikeView, LikedFQIDView

"""
for post urls that start with api/authors/
"""
urlpatterns = [
    # Comment URLs   
    path('<uuid:author_serial>/commented/', CommentedView.as_view(), name='commented'),
    path('<uuid:author_serial>/posts/<uuid:post_id>/comments/', CommentsView.as_view(), name='get_post_comments'),

    # Like URLs
    path('<uuid:author_serial>/liked/', LikedView.as_view(), name='liked'),
    path('<uuid:author_serial>/liked/<uuid:like_serial>/', LikeView.as_view(), name='like'),
    path('<uuid:author_serial>/posts/<uuid:post_id>/likes/', LikesView.as_view(), name='post_likes'),
    path('<uuid:author_id>/posts/<uuid:post_id>/comments/<uuid:comment_id>/likes/', LikedCommentsView.as_view(), name='comment_likes'),
    path('<path:author_fqid>/liked/', LikedFQIDView.as_view(), name='liked_fqid'),
]
