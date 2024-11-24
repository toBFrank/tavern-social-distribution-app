from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    FollowerView, 
    AuthorsView,
    UnfollowView,
    FollowersDetailView,
    FriendsView,
    GetRemoteAuthorsView
)

"""
for user urls that start with api/authors/
"""
urlpatterns = [
    path('', AuthorsView.as_view(), name='authors-list'),
    path('<str:author_id>/followers/<str:follower_id>/', FollowerView.as_view(), name='manage_follow_request'), #Manage Follow Request
    path('<str:author_id>/followers/<str:follower_id>/unfollow/', UnfollowView.as_view(), name='unfollow'),
    path('<str:author_id>/followers/', FollowersDetailView.as_view(), name='followers'),
    path('<str:author_id>/friends/', FriendsView.as_view(), name='friends'),
    path('get_remote_authors/', GetRemoteAuthorsView.as_view(), name='remote_authors'),
]