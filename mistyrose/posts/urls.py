from django.urls import path
from .views import AuthorPostsView, PostDetailsByFqidView, PostImageView, CommentsByFQIDView, PublicPostsView, LikesViewByFQIDView
urlpatterns = [
    # Post URLs
    path('<uuid:post_fqid>/', PostDetailsByFqidView.as_view(), name='post-detail-fqid'),
    path('', PublicPostsView.as_view(), name='public-posts'),  
    
    # Comment URLs
    path('<path:post_fqid>/comments/', CommentsByFQIDView.as_view(), name='get_comments_fqid'),
      
    # Like URLs
    path('<path:post_fqid>/likes/', LikesViewByFQIDView.as_view(), name='get_likes_fqid')
]
