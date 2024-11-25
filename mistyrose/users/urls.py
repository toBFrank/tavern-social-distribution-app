from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    LoginView,
    SignUpView,
    AuthorDetailView,
    LogoutView,
    AuthorProfileView,
    AuthorEditProfileView,
    VerifyTokenView,
    ProfileImageUploadView,
    FollowersDetailView,
    FriendsView,
    FollowingDetailView,
    GetRemoteAuthorsView
)

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),  # Use JWT for login
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),  # Refresh JWT token endpoint
    path('verify/', VerifyTokenView.as_view(), name='verify-token'),  # Verify JWT token endpoint
    path('signup/', SignUpView.as_view(), name='signup'),  # User signup endpoint
    path('logout/', LogoutView.as_view(), name='logout'),  # User logout endpoint
    path('authors/all/', GetRemoteAuthorsView.as_view(), name='all-authors'),
   
    path('authors/<str:username>/upload_image/', ProfileImageUploadView.as_view(), name='upload-profile-image'),
   
    path('authors/<uuid:pk>/profile/edit/', AuthorEditProfileView.as_view(), name='author-edit-profile'),  # Edit author profile
    path('authors/<uuid:pk>/profile/', AuthorProfileView.as_view(), name='author-profile'),  # Author profile view
    path('authors/<uuid:pk>/followers/', FollowersDetailView.as_view(), name='author-followers'),  # Followers endpoint
    path('authors/<uuid:pk>/friends/', FriendsView.as_view(), name='author-friends'),  # Friends endpoint
    path('authors/<uuid:pk>/following/', FollowingDetailView.as_view(), name='author-following'),  # Friends endpoint
   
    path('authors/<path:pk>/profile/edit/', AuthorEditProfileView.as_view(), name='author-edit-profile-fqid'),  # Edit author profile
    path('authors/<path:pk>/profile/', AuthorProfileView.as_view(), name='author-profile-fqid'),  # Author profile view
    path('authors/<path:pk>/followers/', FollowersDetailView.as_view(), name='author-followers-fqid'),  # Followers endpoint
    path('authors/<path:pk>/friends/', FriendsView.as_view(), name='author-friends-fqid'),  # Friends endpoint
    path('authors/<path:pk>/following/', FollowingDetailView.as_view(), name='author-following-fqid'),  # Friends endpoint
    path('authors/<path:pk>/', AuthorDetailView.as_view(), name='author-detail'),  # Author detail view
]