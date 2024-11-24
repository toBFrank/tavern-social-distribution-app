from django.urls import path
from .views import AuthorPostsView, GitHubEventsView, PostDetailsByFqidView, PostImageView, CommentsByFQIDView, PublicPostsView, LikesViewByFQIDView
urlpatterns = [
    # Post URLs
    path('<path:post_fqid>/', PostDetailsByFqidView.as_view(), name='post-detail-fqid'),
    path('', PublicPostsView.as_view(), name='public-posts'),
    path('github/events/<str:username>/', GitHubEventsView.as_view(), name='github-events'),
    
    # Comment URLs
    path('<path:post_fqid>/comments/', CommentsByFQIDView.as_view(), name='get_comments_fqid'),
      
    # Like URLs
    path('<path:post_fqid>/likes/', LikesViewByFQIDView.as_view(), name='get_likes_fqid')
]
