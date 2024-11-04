from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    LoginView,
    SignUpView,
    AuthorDetailView,
    LogoutView,
    # send_follow_request,
    # manage_follow_request,
    AuthorProfileView,
    AuthorEditProfileView,
    VerifyTokenView,
    FollowerView, 
    AuthorsView,
    UnfollowView,
    FollowersDetailView,
    FriendsView,
    ProfileImageUploadView
)

urlpatterns = [
    path('api/login/', LoginView.as_view(), name='login'),  # Use JWT for login
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),  # Refresh JWT token endpoint
    path('verify/', VerifyTokenView.as_view(), name='verify-token'),  # Verify JWT token endpoint
    path('api/signup/', SignUpView.as_view(), name='signup'),  # User signup endpoint
    path('api/authors/<uuid:pk>/', AuthorDetailView.as_view(), name='author-detail'),  # Author detail view
    path('logout/', LogoutView.as_view(), name='logout'),  # User logout endpoint
    path('api/authors/<uuid:pk>/profile/', AuthorProfileView.as_view(), name='author-profile'),  # Author profile view
    path('api/authors/<uuid:pk>/profile/edit/', AuthorEditProfileView.as_view(), name='author-edit-profile'),  # Edit author profile
    path('api/authors/<str:author_id>/followers/<str:follower_id>/', FollowerView.as_view(), name='manage_follow_request'), #Manage Follow Request
    path('api/authors/', AuthorsView.as_view(), name='authors-list'),
    path('authors/<str:author_id>/followers/<str:follower_id>/unfollow/', UnfollowView.as_view(), name='unfollow'),
    path('followers/', FollowersDetailView.as_view(), name='followers'),
    path('friends/', FriendsView.as_view(), name='friends'),
    path('authors/<str:username>/upload_image/', ProfileImageUploadView.as_view(), name='upload-profile-image'),
]