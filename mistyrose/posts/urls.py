from django.urls import path
from .views import AllPostsView, AuthorPostsView, PostDetailsByFqidView, PostDetailsView, PostImageView

urlpatterns = [
    # Post URLs
    path('authors/<uuid:author_serial>/posts/<uuid:post_serial>/', PostDetailsView.as_view(), name='post-detail'),
    path('posts/<uuid:post_fqid>/', PostDetailsByFqidView.as_view(), name='post-detail-fqid'),
    path('authors/<uuid:author_serial>/posts/', AuthorPostsView.as_view(), name='author-posts'),
    path('authors/<uuid:author_serial>/posts/<uuid:post_serial>/image/', PostImageView.as_view(), name='post-image'),
    # Comment URLs
    # Like URLs
]