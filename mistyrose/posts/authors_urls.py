from django.urls import path
from .views import CommentedView, LikedView, LikesView
urlpatterns = [
    # Comment URLs   
    path('<uuid:author_serial>/commented/', CommentedView.as_view(), name='commented'),
    path('<uuid:author_serial>/posts/<uuid:post_id>/comments/', CommentedView.as_view(), name='post_comments'),
    # Like URLs
    path('<uuid:author_serial>/liked/', LikedView.as_view(), name='liked'),
    path('<uuid:author_serial>/posts/<uuid:post_id>/likes/', LikesView.as_view(), name='post_likes'),
    
]
