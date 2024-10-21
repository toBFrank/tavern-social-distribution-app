from django.urls import path
from .views import AuthorPostsView, PostDetailsByFqidView, PostDetailsView, PostImageView, CommentedView
urlpatterns = [
    # Post URLs
    path('authors/<uuid:author_serial>/posts/<uuid:post_serial>/', PostDetailsView.as_view(), name='post-detail'),
    path('<uuid:post_fqid>/', PostDetailsByFqidView.as_view(), name='post-detail-fqid'),
    path('authors/<uuid:author_serial>/posts/', AuthorPostsView.as_view(), name='author-posts'),
    path('authors/<uuid:author_serial>/posts/<uuid:post_serial>/image/', PostImageView.as_view(), name='post-image'),
    # Comment URLs
    # path('api/authors/<uuid:author_serial>/commented/', CommentedView.as_view(), name='commented'),
 
    
    # Like URLs
]
