from django.urls import path
from .views import AuthorPostsView, PostDetailsByFqidView, PostDetailsView, PostImageView, CommentsByFQIDView, PublicPostsView, LikesViewByFQIDView
urlpatterns = [
    # Post URLs
    path('authors/<uuid:author_serial>/posts/<uuid:post_serial>/', PostDetailsView.as_view(), name='post-detail'),
    path('<uuid:post_fqid>/', PostDetailsByFqidView.as_view(), name='post-detail-fqid'),
    path('authors/<uuid:author_serial>/posts/', AuthorPostsView.as_view(), name='author-posts'),
    path('authors/<uuid:author_serial>/posts/<uuid:post_serial>/image/', PostImageView.as_view(), name='post-image'),
    path('', PublicPostsView.as_view(), name='public-posts'),  
    
    # Comment URLs
    path('<path:post_fqid>/comments/', CommentsByFQIDView.as_view(), name='get_comments_fqid'),
      
    # Like URLs
    path('<path:post_fqid>/likes/', LikesViewByFQIDView.as_view(), name='get_likes_fqid')
]
